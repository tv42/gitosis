import os, logging
from ConfigParser import NoSectionError, NoOptionError

from gitosis import group

def haveAccess(config, user, mode, path):
    """
    Map request for write access to allowed path.

    Note for read-only access, the caller should check for write
    access too.

    Returns ``None`` for no access, or a tuple of toplevel directory
    containing repositories and a relative path to the physical repository.
    """
    log = logging.getLogger('gitosis.access.haveAccess')

    log.debug(
        'Access check for %(user)r as %(mode)r on %(path)r...'
        % dict(
        user=user,
        mode=mode,
        path=path,
        ))

    basename, ext = os.path.splitext(path)
    if ext == '.git':
        log.debug(
            'Stripping .git suffix from %(path)r, new value %(basename)r'
            % dict(
            path=path,
            basename=basename,
            ))
        path = basename

    # First test an explicit '[user %s]' section
    log.debug(
        'Checking for explicit access for %(user)r as %(mode)r on %(path)r'
	% dict(
        user=user,
        mode=mode,
        path=path,
        ))

    try:
	repos = config.get('user %s' % user, mode)
    except (NoSectionError, NoOptionError):
        repos = []
    else:
        log.debug(
            'Found section for %(user)r as %(mode)r = %(repos)r'
            % dict(
            user=user,
            mode=mode,
            repos=repos,
            ))
        repos = repos.split()

    mapping = None
    groupname = None

    if path in repos:
            log.debug(
                'Explicit access ok for %(user)r as %(mode)r on %(path)r'
                % dict(
                user=user,
                mode=mode,
                path=path,
                ))
            mapping = path
    else:
        # then go in old code
        for groupname in group.getMembership(config=config, user=user):
            try:
                repos = config.get('group %s' % groupname, mode)
            except (NoSectionError, NoOptionError):
                repos = []
            else:
                repos = repos.split()        

            mapping = None        
            if path in repos:
                log.debug(
                    'Access ok for %(user)r as %(mode)r on %(path)r'
                    % dict(
                    user=user,
                    mode=mode,
                    path=path,
                    ))
                mapping = path
                break
            else:
                try:
                    mapping = config.get('group %s' % groupname,
                                         'map %s %s' % (mode, path))
                except (NoSectionError, NoOptionError):
                    pass
                else:
                    log.debug(
                        'Access ok for %(user)r as %(mode)r on %(path)r=%(mapping)r'
                        % dict(
                        user=user,
                        mode=mode,
                        path=path,
                        mapping=mapping,
                        ))
                    break

    # If we used a [user _] section, we consider being in the 'gitosis' group
    if groupname is None:
        groupname = 'gitosis'

    if mapping is not None:
        prefix = None
        try:
            prefix = config.get(
                'group %s' % groupname, 'repositories')
        except (NoSectionError, NoOptionError):
            try:
                prefix = config.get('gitosis', 'repositories')
            except (NoSectionError, NoOptionError):
                prefix = 'repositories'

        log.debug(
            'Using prefix %(prefix)r for %(path)r'
            % dict(
            prefix=prefix,
            path=mapping,
            ))
        return (prefix, mapping)
