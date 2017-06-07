# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Distributed under terms of the GNU GPLv3 license.

from __future__ import print_function
try:
    from urllib.parse import urljoin, urlparse
except ImportError:
    from urlparse import urljoin, urlparse
import argparse
import json
import logging
import os
import signal
import sys

import magic
import requests

class FileTeaClient(object):
    """Base client class for FileTea access"""
    def __init__(self, url=None):
        logger = logging.getLogger('filetea.FileTeaClient')
        # Set URL to default if not URL is passed
        self.url = 'https://filetea.me/' if url is None else url
        logger.debug('Using FileTea server {}'.format(self.url))
        self.session = requests.session()

    def get_peer_id(self):
        """
        Perform handshake with endpoint to get a usable peer-id

        :return: peer-id
        :rtype: string
        """
        logger = logging.getLogger('filetea.FileTeaClient.get_peer_id')
        handshake_headers = {'Content-Type': 'text/plain'}
        handshake_text = '{"mechanisms":["websocket","long-polling"],"url":"/transport/"}'
        url = urljoin(self.url, 'transport/handshake')
        handshake = self.session.post(url, data=handshake_text, headers=handshake_headers)
        logger.debug(handshake.headers)
        logger.debug(handshake.content)
        return handshake.json()['peer-id']

    def register_file(self, peer_id, file_to_send):
        """
        Register file with endpoint and returns url to use to download the file

        :return: url
        :rtype: string
        """
        logger = logging.getLogger('filetea.FileTeaClient.register_file')
        file_name = os.path.basename(file_to_send)
        file_size = os.path.getsize(file_to_send)
        if hasattr(magic, 'open'): # use magic-file-extensions
            ms = magic.open(magic.MIME_TYPE)
            ms.load()
            mime_type = ms.file(file_to_send)
            ms.close()
        else: # use python-magic
            mime_type = magic.from_file(file_to_send, mime=True)
        send_headers = {'Content-Type': 'text/plain'}
        send_url = urljoin(self.url, 'transport/lp/send')
        send_data = {
                "method": "addFileSources",
                "params": [[
                    file_name,
                    mime_type,
                    file_size
                          ]],
                "id": "1" }
        send_data = 'X{}'.format(json.dumps(send_data))
        logger.info('Sending: {}'.format(send_data))
        send_response = self.session.post(send_url, data=send_data, params=peer_id, headers=send_headers)
        logger.debug(send_response.headers)
        logger.debug(send_response.text)
        send_response_text = send_response.text
        assert send_response_text.startswith('@')
        send_response_text = send_response_text[1:]
        send_response_json = json.loads(send_response_text)
        logger.debug('Decoded JSON response: {}'.format(send_response_json))
        file_download_url = urljoin(self.url, send_response_json['result'][0][0])
        return file_download_url

    def send_file(self, file_to_send, token):
        """
        Send specified file to endpoint
        """
        logger = logging.getLogger('filetea.FileTeaClient.send_file')
        logger.info('Sending file {} to {}'.format(file_to_send, token))
        send_url = urljoin(self.url, token)
        with open(file_to_send, 'rb') as f:
            send_response = self.session.put(send_url, f)
        logger.debug(send_response)

    def receive_response(self, peer_id, file_to_send):
        """
        Wait for server response to send file
        """
        logger = logging.getLogger('filetea.FileTeaClient.receive_response')
        receive_url = urljoin(self.url, 'transport/lp/receive')
        receive_response = self.session.get(receive_url, params=peer_id)
        receive_response_text = receive_response.text
        logger.debug(receive_response_text)
        try:
            receive_response_text = receive_response_text[1:]
            receive_response_json = json.loads(receive_response_text)
            logger.debug('Decoded JSON response: {}'.format(receive_response_json))
            if receive_response_json['method'] == 'fileTransferNew':
                token = receive_response_json['params'][-1]
                logger.debug('Got a file transfer request from token {}'.format(token))
                print('File transfer request received from token {}'.format(token))
                self.send_file(file_to_send, token)
            else:
                logger.info('Not a file transfer request')
        except Exception as e:
            logger.info('Not a file transfer request: {}'.format(e))
            pass

def exit(signal, frame):
    sys.exit(0)

def run(args):
    logger = logging.getLogger('filetea')
    # Set FileTea server URL
    server_url = args.url if args.url != None else os.getenv('FILETEAURL', 'https://filetea.me/')
    if not urlparse(server_url).netloc:
        sys.exit('No schema supplied on URL.')

    file_tea_client = FileTeaClient(server_url)
    # Get a peer-id registered with endpoint
    peer_id = file_tea_client.get_peer_id()
    # Register specified file with endpoint, which returns the URL to download the file
    file_url = file_tea_client.register_file(peer_id, args.file)
    logger.info('URL for file {}: {}'.format(args.file, file_url))
    print('URL: {}'.format(file_url))
    print('Press CTRL+C to stop sharing...')

    while True:
        # Main loop
        logger.info('Waiting for a server response')
        file_tea_client.receive_response(peer_id, args.file)

def main():
    signal.signal(signal.SIGINT, exit)
    parser = argparse.ArgumentParser(description='Easy file transfer using the FileTea service')
    parser.add_argument('--url', '-l', help='filetea server url (also FILETEAURL)')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='be verbose (vv to increase verbosity)')
    parser.add_argument('file', help='file to send')
    parser.set_defaults(func=run)
    args = parser.parse_args()

    # Set loglevel equivalents
    log_levels = {
            0: logging.ERROR,
            1: logging.INFO,
            2: logging.DEBUG }

    # Maximum loglevel is 2 if user sends more vvv we ignore it
    args.verbose = 2 if args.verbose >= 2 else args.verbose
    logging.basicConfig(level=log_levels[args.verbose])

    # Check if file exists and can be read
    if not os.path.exists(args.file):
        sys.exit('File does not exist.')
    if not os.path.isfile(args.file):
        sys.exit('Path is not a file.')
    if not os.access(args.file, os.R_OK):
        sys.exit('File can not be read.')

    args.func(args)
