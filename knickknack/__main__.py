#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import argparse 
import logging

import requests

import knickknack

## ┏┳┓┏━┓╻┏┓╻
## ┃┃┃┣━┫┃┃┗┫
## ╹ ╹╹ ╹╹╹ ╹

def main():  # pragma: no cover

    logging.basicConfig()

    logger = logging.getLogger('knickknack')

    parser = \
        argparse.ArgumentParser(description=knickknack.__description__)

    parser.add_argument('-a', '--app-id', type=str,
                        help='KnockHQ Application ID', required=True)
    parser.add_argument('-k', '--api-key', type=str,
                        help='KnockHQ API Key', required=True)
    parser.add_argument('-p', '--path', type=str,
                        help='Output Path')
    parser.add_argument('-f', '--format', type=str,
                        help='Output Format', default='csv', choices=['csv', 'json'])
    parser.add_argument('object_id', nargs="+", type=int,
                        help='KnockHQ Object Number')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='debug')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info(repr(args))

    collections = []

    session = requests.Session()

    session.headers.update({
        'X-Knack-Application-Id': args.app_id,
        'X-Knack-REST-API-Key': args.api_key,
    })

    for object_id in args.object_id:

        url = '%s/objects/object_%d/records/export/applications/%s?type=%s' % (knickknack.KNACKHQ_API_URI, object_id, args.app_id, args.format)

        r = session.get(url, stream=True)

        filename = r.headers['content-disposition'].replace('attachment; filename=','').strip('"')

        filepath = os.path.join(args.path, filename)
        output = open(filepath, 'w')

        logger.info('Downloading %s (%d)' % (filepath, object_id))

        while True:
            buffer = r.raw.read(10000)

            if not buffer:
                break

            if type(buffer) != type(''):
                buffer = buffer.decode('utf-8')

            output.write(buffer)

if __name__ == '__main__':
    sys.exit(main())

