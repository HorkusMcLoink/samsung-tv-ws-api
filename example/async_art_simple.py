#!/usr/bin/env python3
# NOTE old api is 2021 and earlier Frame TV's, new api is 2022+ Frame TV's

import os
import asyncio
import logging
import argparse

from samsungtvws.async_art import SamsungTVAsyncArt
from samsungtvws import exceptions

from samsungtvws.async_remote import SamsungTVWSAsyncRemote
from samsungtvws.remote import SendRemoteKey

def parseargs():
    # Add command line argument parsing
    parser = argparse.ArgumentParser(description='Example async art Samsung Frame TV.')
    parser.add_argument('ip', action="store", type=str, default=None, help='ip address of TV (default: %(default)s))')
    parser.add_argument('-D','--debug', action='store_true', default=False, help='Debug mode (default: %(default)s))')
    return parser.parse_args()
    
async def main():
    args = parseargs()
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
                        level=logging.DEBUG) # or logging.INFO
    logging.debug('debug mode')
    token_file = "token_file.txt"

    if not os.path.isfile(token_file):
        logging.info('fetching token')
        tvr = SamsungTVWSAsyncRemote(host=args.ip, port=8002, token_file=token_file)
        await tvr.start_listening()
        await tvr.close()
    else:
        logging.info('token file exists')

    try:
        logging.info('opening art websocket with token')
        tv = SamsungTVAsyncArt(host=args.ip, port=8002, token_file=token_file)
        await tv.start_listening()
    except Exception as e:
        logging.exception(e)
        logging.warning('trying with BOTH websockets open')
        tvr = SamsungTVWSAsyncRemote(host=ip, port=8002, token_file=token_file)
        await tvr.start_listening()
        tv = SamsungTVAsyncArt(host=args.ip, port=8002)
        await tv.start_listening()
        await tvr.close()
    
    logging.info('getting tv info')
    #is art mode supported
    supported = await tv.supported()
    logging.info('art mode is supported: {}'.format(supported))
    
    if supported:
        try:
            #is tv on (calls tv rest api)
            tv_on = await tv.on()
            logging.info('tv is on: {}'.format(tv_on))
            
            #is art mode on
            art_mode = await tv.get_artmode()                  #calls websocket command to determine status
            logging.info('art mode is on: {}'.format(art_mode))
            
            #is tv on and in art mode
            art_mode = await tv.in_artmode()                   #calls rest api and websocket command to determine status
            logging.info('TV is in art mode: {}'.format(art_mode))

            #get api version 4.3.4.0 is new api, 2.03 is old api
            api_version = await tv.get_api_version()
            logging.info('api version: {}'.format(api_version))
            
            # Request list of all art
            try:
                info = await tv.available()
                #info = await tv.available('MY-C0002')              #gets list of uploaded art, MY-C0004 is favourites
            except AssertionError:
                info='None'
            logging.info('artwork available on tv: {}'.format(info))

            # Request current art
            info = await tv.get_current()
            logging.info('current artwork: {}'.format(info))
            content_id = info['content_id']                         #example to get current content_id
            
        except exceptions.ResponseError as e:
            logging.warning('ERROR: {}'.format(e))
        except AssertionError as e:
            logging.warning('no data received: {}'.format(e))

    await tv.close()


asyncio.run(main())
