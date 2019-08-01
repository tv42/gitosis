"""
Perform gitosis actions for a git hook.
"""

import errno
import logging
import os
import sys
import shutil

from gitosis import repository
from gitosis import ssh
from gitosis import ssh_principals
from gitosis import gitweb
from gitosis import gitdaemon
from gitosis import app
from gitosis import util


def serve_principal(sshUser, principals):
    TEMPLATE=('command="gitosis-serve %(user)s",no-port-forwarding,'
              +'no-X11-forwarding,no-agent-forwarding,no-pty %(principals)s')

    for (sshUser, principals) in keys:
        log.debug(TEMPLATE % dict(user=user))
        print TEMPLATE % dict(user=user, principals=principals)


class Main(app.App):
    def create_parser(self):
        parser = super(Main, self).create_parser()
        parser.set_usage('%prog [OPTS] sshUser principal principal ...')
        parser.set_description(
            'Serves principals as AuthorizedPrincipalsCommand ')
        return parser

    def handle_args(self, parser, cfg, options, args):
        try:
            sshUser = args.pop(0)
            principals = ' '.join(args)
        except ValueError:
            parser.error('Missing argument sshUsers and/or principals.')

        log = logging.getLogger('gitosis.principals')

        if sshUser != "":
            log.info('Running serve_principal for user %s', sshUser)
            serve_principal(sshUser, principals)
            log.info('Done.')

#        if git_dir is None:
#            log.error('Must have GIT_DIR set in enviroment')
#            sys.exit(1)
#
#        if hook == 'post-update':
#            log.info('Running hook %s', hook)
#            post_update(cfg, git_dir)
#            log.info('Done.')
#        else:
#            log.warning('Ignoring unknown hook: %r', hook)
