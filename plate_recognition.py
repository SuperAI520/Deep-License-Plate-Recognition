#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import argparse
import json
import time
from collections import OrderedDict
from glob import glob

import requests


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        'Read license plates from images and output the result as JSON.',
        epilog=
        'For example: python plate_recognition.py --api MY_API_KEY "/path/to/vehicle-*.jpg"'
    )
    parser.add_argument('--api', help='Your API key.', required=True)
    parser.add_argument('--region', help='Match the license plate pattern fo specific region', required=False)
    parser.add_argument('--url', default='http://localhost:8080', help="Url to self hosted sdk", required=False)
    parser.add_argument('files', nargs='+', help='Path to vehicle image or pattern.')
    return parser.parse_args()


def main():
    args = parse_arguments()
    result = []
    paths = args.files
    region = args.region
    if len(paths) == 0:
        print('File {} does not exist.'.format(args.FILE))
        return
    for path in paths:
        with open(path, 'rb') as fp:
            if args.url:
                response = requests.post(args.url + '/alpr', files=dict(upload=fp), data=dict(regions=region))
            else:    
                response = requests.post(
                    'https://api.platerecognizer.com/v1/plate-reader/',
                    files=dict(upload=fp),
                    data=dict(regions=region),
                    headers={'Authorization': 'Token ' + args.api})
            result.append(response.json(object_pairs_hook=OrderedDict))
            time.sleep(1)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
