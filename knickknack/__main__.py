#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import argparse 
import pprint
import logging

import requests

import csv

try:
    import xlwt3 as xlwt
except ImportError:
    import xlwt

try:
    import urllib.parse as urlparse
except:
    import urlparse

import knickknack

fieldmap = {
    'Street': 'street',
    'Street Cont.': 'street2',
    'City': 'city',
    'State': 'state',
    'ZIP': 'zip',
    'Title': 'title',
    'First': 'first',
    'Middle': 'middle',
    'Last': 'last',
    'Email': 'email',
    'ID': 'id',
    'Identifier': 'identifier',
}

#from collections import OrderedDict

logger = logging.getLogger('knickknack')

class Collection(object):
    def __init__(self, object_id, app_id, api_key):
        self.name = ''
        self.fields = []
        self.records = []
        self.object_id = object_id
        self.app_id = app_id
        self.api_key = api_key
        self.request_headers = {
            'X-Knack-Application-Id': self.app_id,
            'X-Knack-REST-API-Key': self.api_key,
        }

        self.headers_ext_flat = []
        self.headers_ext = []
        self.headers = []

    def initialize(self):

        s = requests.Session()

        s.headers.update(self.request_headers)

        logger.info('Downloading object_%d configuration' % self.object_id)

        url = urlparse.urljoin(knickknack.KNOCKHQ_API_URI, 'objects/object_%d' % self.object_id)

        r = s.get(url)
        j = r.json()

        self.name = j['object']['name']

        self.fields = j['object']['fields']

        logger.info('Downloading object_%d rows' % self.object_id)

        url = urlparse.urljoin(knickknack.KNOCKHQ_API_URI, 'objects/object_%d/records' % self.object_id)

        r = s.get(url, params={'format': 'raw', 'rows_per_page': 1000000, 'page': 1})
        j = r.json()

        for record in j['records']:
            #Process some maximum values as needed
            #...           
            self.records.append(record)

    def prep_headers(self):
        
        for field in self.fields:
            options = [field['name']]
            func = lambda x: x
            multi = False
            dicted = False
            array = False

            if field['type'] in ['multiple_choice']:
                if isinstance(field['format']['options'], type([])):
                    options = field['format']['options']
                else:
                    options = [field['format']['options']]
                multi = True

            if field['type'] in ['address']:
                options = [
                    'Street',
                    'Street Cont.',
                    'City',
                    'State',
                    'ZIP',
                ]

                multi = True
                dicted = True

            if field['type'] in ['name']:
                options = [
                    'Title',
                    'First',
                    'Middle',
                    'Last',
                ]

                multi = True
                dicted = True

            if field['type'] in ['email']:
                options = [
                    'Email',
                ]

                dicted = True

            if field['type'] in ['connection']:
                options = [
                    'ID',
                    'Identifier',
                ]

                dicted = True
                array = True

            for option in options:
                header = {}
                header['field'] = field
                header['name'] = option
                header['func'] = func
                header['multi'] = multi
                header['dicted'] = dicted
                header['array'] = array

                self.headers.append(header)

            self.headers_ext_flat.append(field['name'])
            for i in range(len(options)-1): self.headers_ext_flat.append(None)

            self.headers_ext.append((field['name'], len(options)))
                

    def export_csv(self, writer, ext_header, collections=None):
        #Allow for cross collection linking for functions.. this is going to hurt
        if not collections:
            collections = {}                

        self.prep_headers()        

        if ext_header:
            writer.writerow(['ID'] + self.headers_ext_flat)
            writer.writerow([None] + [x['name'] if x['name'] != x['field']['name'] else '...' for x in self.headers])
        else:
            writer.writerow(['ID'] + [x['name'] for x in self.headers])

        for record in self.records:
            data = [[record['id']]]

            for header in self.headers:

                if header['multi']:
                    if header['dicted']:
                        if record[header['field']['key']]:
                            value = [record[header['field']['key']].get(fieldmap[header['name']])]                                
                        else:
                            value = [None]
                    else:
                        value = ['x' if header['name'] in record[header['field']['key']] else None]
                else:
                    if header['dicted']:
                        if record[header['field']['key']]:
                            if header['array']:
                                value = [x.get(fieldmap[header['name']]) for x in record[header['field']['key']]]
                            else:
                                value = [record[header['field']['key']].get(fieldmap[header['name']])]
                        else:
                            value = [None]
                    else:
                        value = [header['func'](record[header['field']['key']])]

                data.append(value)

            span = max([len(x) for x in data])
            for s in range(span):
                _data = []
                for e, d in enumerate(data):
                    try:
                        value = d[s]
                    except:
                        if e == 0:
                            value = '...'
                        else:
                            value = None

                    _data.append(value)
                writer.writerow(_data)

    def export_xml(self, worksheet, ext_header, collections=None):
        #Reserved for refactored export later on (with linking and multiple work sheets)
        pass
        
## ┏┳┓┏━┓╻┏┓╻
## ┃┃┃┣━┫┃┃┗┫
## ╹ ╹╹ ╹╹╹ ╹

def main():  # pragma: no cover

    logging.basicConfig()

    parser = \
        argparse.ArgumentParser(description=knickknack.__description__)

    parser.add_argument('-a', '--app-id', type=str,
                        help='KnockHQ Application ID', required=True)
    parser.add_argument('-k', '--api-key', type=str,
                        help='KnockHQ API Key', required=True)
    parser.add_argument('-p', '--path', type=str,
                        help='Output Path')
    parser.add_argument('-f', '--format', type=str,
                        help='Output Format', default='csv', choices=['csv'])
    parser.add_argument('-H', '--ext-header', action='store_true',
                        help='Extended Header', default=False)
    parser.add_argument('object_id', nargs="+", type=int,
                        help='KnockHQ Object Number')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='debug')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info(repr(args))

    collections = []

    for object_id in args.object_id:
        #print(object)
        #print(urlparse.urljoin(knickknack.KNOCKHQ_API_URI, 'objects/object_%d' % object))
        collection = Collection(object_id, args.app_id, args.api_key)
        collection.initialize()

        collections.append(collection)

    for collection in collections:

        if args.format == 'csv':
            logger.info('Exporting Collection %s' % collection.name)
            filename = os.path.join(args.path, collection.name + '.csv')

            writer = csv.writer(open(filename, 'w'))

            collection.export_csv(writer=writer, ext_header=args.ext_header)


if __name__ == '__main__':
    sys.exit(main())

