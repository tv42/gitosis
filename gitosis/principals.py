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
from gitosis import gitweb
from gitosis import gitdaemon
from gitosis import app
from gitosis import util


def serve_principal(cfg, sshUser, principals):

    TEMPLATE=('command="gitosis-serve %(user)s",no-port-forwarding,'
              +'no-X11-forwarding,no-agent-forwarding,no-pty %(principals)s')

    for p in   util.getAllowedSSHPrincipals(config=cfg).split()  : 
        print(TEMPLATE % dict(user=sshUser.partition('@')[0], principals=p))

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
            #log.debug('serve_principal: %s', serve_principal(cfg, sshUser, principals))
            serve_principal(cfg, sshUser, principals)
            log.info('Done.')
