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

def serve_principal(sshUser, principal):
    print "Do nothing"

def post_update(cfg, git_dir):
    export = os.path.join(git_dir, 'gitosis-export')
    try:
        shutil.rmtree(export)
    except OSError, e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise
    repository.export(git_dir=git_dir, path=export)
    os.rename(
        os.path.join(export, 'gitosis.conf'),
        os.path.join(export, '..', 'gitosis.conf'),
        )
    # re-read config to get up-to-date settings
    cfg.read(os.path.join(export, '..', 'gitosis.conf'))
    gitweb.set_descriptions(
        config=cfg,
        )
    generated = util.getGeneratedFilesDir(config=cfg)
    gitweb.generate_project_list(
        config=cfg,
        path=os.path.join(generated, 'projects.list'),
        )
    gitdaemon.set_export_ok(
        config=cfg,
        )
    authorized_keys = util.getSSHAuthorizedKeysPath(config=cfg)
    ssh.writeAuthorizedKeys(
        path=authorized_keys,
        keydir=os.path.join(export, 'keydir'),
        )
    principals = util.getSSHPrincipalsPath(config=cfg)
    ssh_principals.writePrincipals(
        path=principals,
        principals=os.path.join(export, 'keydir/principals'),
        )

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
            parser.error(principals)
        except ValueError:
            parser.error('Missing argument sshUsers and/or principals.')

        log = logging.getLogger('gitosis.principals')
        os.umask(0022)

        git_dir = os.environ.get('GIT_DIR')

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
