#!/usr/bin/env python
import os
import sys
import glob
import re
import shutil
import glob
from optparse import OptionParser

def main():
    (options, maildir) = checkArgs()

    if options.recursive:
        checkMaildirFolders(maildir, options.quiet, options.fix)

    else:
        maildir_contents = os.listdir(maildir)
        if not ('cur' in maildir_contents and 'new' in maildir_contents and
                'tmp' in maildir_contents):
            print >> sys.stderr, ('Missing cur, new, and/or tmp. Are you' +
                    'this is a maildir?')
            sys.exit(1)
        for subdir in ['cur/', 'new/', 'tmp/']:
            checkMailSize(maildir + subdir, options.quiet, options.fix)

def checkArgs():
    parser = OptionParser(usage='%prog [options] path_to_maildir')

    parser.add_option('-f', '--fix', dest='fix', default=False,
        action='store_true', help='Execute the calculated mv commands')

    parser.add_option('-q', '--quiet', dest='quiet', default=False,
        action='store_true', help='Don\'t display any output.')

    parser.add_option('-r', '--recursive', dest='recursive', default=False,
        action='store_true', help='Recursively process all extra folders in' +
            'the given maildir.')

    (options, args) = parser.parse_args()

    # We only want the path as an argument.
    if len(args) > 1:
        parser.error('Too many arguments')

    # We actually need the path as an argument.
    if len(args) < 1:
        parser.error('Please provide a path to the maildir')

    # Technically not wrong, but a stupid combination of options
    if options.quiet and not options.fix:
        parser.error('Specifying -q without -f effectively does noting '+
                'so I\'ll just exit here')

    # Grab the maildir path
    maildir = args[0]

    # Make sure the directory has a trailing slash.
    if not maildir[len(maildir)-1] == '/':
        maildir = maildir + '/'

    return (options, maildir)

def checkMaildirFolders(dirpath, quiet=False, fix=False):

    subdirs = glob.glob(dirpath + '.*')

    for subdir in subdirs:
        if (os.path.isdir(subdir) and os.path.isfile(subdir +
            '/maildirfolder')):
            checkMaildirFolders(subdir + '/', quiet, fix)

    for subdir in ['cur/', 'new/', 'tmp/']:
        checkMailSize(dirpath + subdir, quiet, fix)


def checkMailSize(dirpath, quiet=False, fix=False):
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
                if fix:
                    shutil.move(dirpath + mail, dirpath +
                        mail.replace("S=" + reported_size, "S=" +
                            str(actual_size)))

main()
