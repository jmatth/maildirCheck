#!/usr/bin/env python
import os
import sys
import glob
import re
import shutil
import glob
import fileinput
from optparse import OptionParser

def main():
    (options, maildir) = checkArgs()

    if options.recursive:
        checkMaildirFolders(maildir, options.quiet, options.fix)

    else:
        checkMailSize(maildir, options.quiet, options.fix)

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

    checkMailSize(dirpath, quiet, fix)


def checkMailSize(dirpath, quiet=False, fix=False):

    mailRegex = re.compile('[0-9]{10}\.M.*,S=[0-9]+:2,S?')

    for subdir in [dirpath + x for x in ['cur/', 'new/', 'tmp/']]:
        for mail in os.listdir(subdir):
            if mailRegex.match(mail):
                reported_size = re.search('[0-9]+',
                        re.search('S=[0-9]+', mail).group()
                        ).group()
                actual_size = str(os.stat(subdir + mail).st_size)

                if not reported_size == actual_size:
                    if not quiet:
                        print ('mv ' + subdir + mail + ' ' + subdir +
                            mail.replace("S=" + reported_size, "S=" +
                                actual_size))
                    if fix:
                        uidLineOld = mail.rsplit(':', 1)[0]
                        uidLineNew = uidLineOld.replace("S=" + reported_size,
                                "S=" + actual_size)

                        shutil.move(subdir + mail, subdir +
                            mail.replace("S=" + reported_size, "S=" +
                                actual_size))

                        for line in fileinput.input(dirpath +
                                'dovecot-uidlist', inplace=1):
                            sys.stdout.write(line.replace(uidLineOld,
                                uidLineNew))

if __name__ == "__main__":
    main()
