#!/usr/bin/env python2.7
from __future__ import print_function

import urllib
import json
import os.path

config_dir = '../configs'

def main():
    for i in range(32):
        print('Getting', i)
        target_base = 'https://pioneers.berkeley.edu/team_config/api/{}/'
        try:
            f = urllib.urlopen(target_base.format(i))
            obj = json.load(f)
            data = obj[u'file_contents']
            with open(os.path.join(config_dir, '{}.cfg'.format(i)), 'w') as wfile:
                wfile.write(data)
        except Exception as ex:
            print("Couldn't query", target_base.format(i), "got", ex)

if __name__ == '__main__':
    main()
