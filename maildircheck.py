#!/usr/bin/env python
import os
import sys
import glob
import re
import shutil
from optparse import OptionParser

def main():
    parser = OptionParser()

    parser.add_option('-d', '--directory', dest='dirname', action='store',
        type='string', help='Path to Maildir to check')

    parser.add_option('-f', '--fix', dest='fix', default=False,
        action='store_true', help='Execute the calculated mv commands')

    parser.add_option('-q', '--quiet', dest='quiet', default=False,
        action='store_true', help='Don\'t display any output.')

    (options, args) = parser.parse_args()

    if options.dirname == None:
        print 'Must provide a path to the Maildir'
        sys.exit()

    # Make sure the directory has a trailing slash.
    if not options.dirname[len(options.dirname)-1] == '/':
        options.dirname = options.dirname + '/'

    maildir_contents = os.listdir(options.dirname)

    if not ('new' in maildir_contents and
            'tmp' in maildir_contents and
            'cur' in maildir_contents):
        print 'Missing cur, new, and/or tmp. Are you sure this is a maildir?'
        sys.exit()

    for subdir in ['new/','tmp/','cur/']:
        checkmail(options.dirname + subdir, options.quiet, options.fix)

def checkmail(dirpath, quiet=True, autofix=False):
    mailRegex = re.compile('[0-9]{10}\.M.*,S=[0-9]+:2,S?')
    for mail in os.listdir(dirpath):
        if mailRegex.match(mail):
            reported_size = re.search('[0-9]+',
                    re.search('S=[0-9]+', mail).group()
                    ).group()
            actual_size = os.stat(dirpath + mail).st_size
            
            if not int(reported_size) == actual_size:
                if not quiet:
                    print ('mv ' + dirpath + mail + ' ' + dirpath +
                        mail.replace("S=" + reported_size, "S=" +
                            str(actual_size)))
                if autofix:
                    shutil.move(dirpath + mail, dirpath +
                        mail.replace("S=" + reported_size, "S=" + actual_size))
main()
