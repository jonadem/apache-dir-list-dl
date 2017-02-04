#!/usr/bin/env python

"""An apache directory listing downloader

This script takes an url as input and download files listed from apache

TODO: Make it more robust to links ending with "/" or not
"""

import os
import sys
import argparse
import re
import urllib2
import pycurl
import errno

PATTERN = r'<img .*? alt="\[(   |DIR)\]">.*?<a href=".*?">(.*?)</a>'

def recursive_dl(url, path):
    """
    If the link is a folder, call this same function on the link.
    If it's a file, download it
    """
    response = urllib2.urlopen(url).read()

    for linktype, name in re.findall(PATTERN, response, re.IGNORECASE):
        print(path, linktype, name)
        if linktype == "   ":
            filepath = path+name
            if not os.path.exists(os.path.dirname(filepath)):
                try:
                    os.makedirs(os.path.dirname(filepath))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(filepath, "wb") as fp:
                curl = pycurl.Curl()
                curl.setopt(pycurl.URL, url+name)
                curl.setopt(pycurl.WRITEDATA, fp)
                curl.perform()
                curl.close()
        elif linktype == "DIR":
            recursive_dl(url+name, path+name)


class ReadableDir(argparse.Action):
    """
    Check that the given argument is a readable directory
    """
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))


def main(arguments):

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('url', help="targetted url")
    parser.add_argument('-o', '--outdir', help="Output directory", action=ReadableDir,
                        default="./")

    args = parser.parse_args(arguments)

    recursive_dl(args.url, args.outdir)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
