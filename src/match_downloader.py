#!/usr/bin/env python2.7
from __future__ import print_function

import urllib
import argparse
import json
import os.path

match_dir = '../matches'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, action='store')
    args = parser.parse_args()
    match_exists = True
    i = args.start
    while match_exists:
        print('Getting', i)
        target_base = \
            'https://pioneers.berkeley.edu/match_schedule/api/match/{}/'
        try:
            f = urllib.urlopen(target_base.format(i))
            data = f.read()
            obj = json.loads(data)
            match_exists = obj.get(u'message', None) == u'success'
            if match_exists:
                with open(os.path.join(match_dir, '{}.match'.format(i)), 'w') as wfile:
                    wfile.write(data)
        except Exception as ex:
            print("Couldn't query", target_base.format(i), "got", ex)
        i += 1


if __name__ == '__main__':
    main()
