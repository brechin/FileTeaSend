#!/usr/bin/env python
from __future__ import print_function
import logging
import sys
import os
import json

import requests
import magic

__FILETEA_URL = 'https://filetea.me/'
logging.basicConfig(level=logging.DEBUG)


def get_peer_id(session_obj):
    """Perform handshake with endpoint to get a usable peer-id"""
    logger = logging.getLogger('get_peer_id')
    handshake_text = '{"mechanisms":["websocket","long-polling"],"url":"/transport/"}'
    handshake = session_obj.post('%stransport/handshake' % __FILETEA_URL, data=handshake_text,
                       headers={'Content-Type': 'text/plain'})
    logger.debug(handshake.headers)
    logger.debug(handshake.content)
    return handshake.json()['peer-id']


def send_file(session_obj, file_name_to_send, token):
    """Send specified file to endpoint"""
    logger = logging.getLogger('send_file')
    logger.debug('Sending %s to %s' % (file_name_to_send, token))
    logger.info('Sending file %s' % file_name_to_send)
    with open(file_name_to_send, 'rb') as f:
        resp = session_obj.put('%s%s' % (__FILETEA_URL, token), f)
    logger.debug(resp)
    return resp


def register_file(session_obj, my_uuid, file_to_send):
    """Register file with endpoint, returns url to use to download the file"""
    logger = logging.getLogger('register_file')
    mime_type = magic.from_file(file_to_send, mime=True)
    send_url = '%stransport/lp/send?%s' % (__FILETEA_URL, my_uuid)
    send_data = 'X{"method":"addFileSources","params":[["%s","%s",%d]],"id":"1"}' % (
        os.path.basename(file_to_send), mime_type, os.path.getsize(file_to_send))
    logger.info('Sending %s' % send_data)
    sent_response = session_obj.post(send_url, data=send_data, headers={'Content-Type': 'text/plain'})
    logger.debug(sent_response.headers)
    logger.debug(sent_response.text)
    send_return_data = sent_response.text
    assert send_return_data.startswith('@')
    send_return_data = send_return_data[1:]
    send_response_json = json.loads(send_return_data)
    logger.debug('Decoded JSON: %s' % send_response_json)
    file_download_url = '%s%s' % (__FILETEA_URL, send_response_json['result'][0][0])
    return file_download_url

def main():
    base_logger = logging.getLogger('filetea')
    session = requests.session()

    if len(sys.argv) < 2:
        sys.exit('Need to specify file to share')

    file_to_send = sys.argv[1]
    if not os.path.exists(file_to_send):
        sys.exit('File does not exist.')
    if not os.path.isfile(file_to_send):
        sys.exit('Path is not a file.')

    # Get a peer-id registered with endpoint
    my_uuid = get_peer_id(session)
    # Register specified file with endpoint, which returns the URL to download the file
    url = register_file(session, my_uuid, file_to_send)
    base_logger.info('URL for file %s: %s' % (file_to_send, url))
    print('URL: %s' % url)

    while True:
        # Try recv, might 404
        base_logger.info('Waiting to send recv')
        recv_url = '%stransport/lp/receive?%s' % (__FILETEA_URL, my_uuid)
        recv_response = session.get(recv_url)
        base_logger.debug(recv_response.content)

        recv_return_data = recv_response.content
        if recv_return_data.startswith(b'y'):
            base_logger.debug('Got file transfer request')
            recv_return_data = recv_return_data[1:]

            r = json.loads(recv_return_data)

            if r['method'] == "fileTransferNew":
                send_file(session, file_to_send, r['params'][-1])
        else:
            base_logger.debug('Not a file transfer')
