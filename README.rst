==========================================================
 ``gitosis`` -- software for hosting ``git`` repositories
==========================================================

	Manage ``git`` repositories, provide access to them over SSH,
	with tight access control and not needing shell accounts.

.. note::

	Documentation is still lacking, and non-default configurations
	(e.g. config file, repositories, installing in a location that
	is not in ``PATH``) basically have not been tested at all.
	Basic usage should be very reliable -- the project has been
	hosting itself for a long time. Any help is welcome.

``gitosis`` aims to make hosting ``git`` repos easier and safer. It
manages multiple repositories under one user account, using SSH keys
to identify users. End users do not need shell accounts on the server,
they will talk to one shared account that will not let them run
arbitrary commands.

``gitosis`` is licensed under the GPL, see the file ``COPYING`` for
more information.

You can get ``gitosis`` via ``git`` by saying::

    This repositories are from jakob@schuerz.at, support python3 and ssh-certificates
    git clone git@codeberg.org:xundeenergie/gitosis.git (fetch)
    git clone git@github.com:xundeenergie/gitosis.git (fetch)
    git clone git@git.schuerz.at:public/gitosis.git (fetch)

    This repository translates gitosis to python3, but not fully.
    git clone git@github.com:mgukov/gitosis.git (push)

    Original repository seems unmaintained
    git clone git@github.com:tv42/gitosis.git (fetch)


And install it via::

    python setup.py install

Though you may want to use e.g. ``--prefix=``.


Setting up
==========

First, we will create the user that will own the repositories. This is
usually called ``git``, but any name will work, and you can have more
than one per system if you really want to. The user does not need a
password, but does need a valid shell (otherwise, SSH will refuse to
work). Don't use an existing account unless you know what you're
doing.

I usually store ``git`` repositories in the subtree
``/srv/example.com/git`` (replace ``example.com`` with your own
domain). You may choose another location. Adjust to suit and run::

	sudo adduser \
	    --system \
	    --shell /bin/sh \
	    --gecos 'git version control' \
	    --group \
	    --disabled-password \
	    --home /srv/example.com/git \
	    git

This command is known to work in Debian and Ubuntu. Your mileage may
vary.

You will need an SSH public key to continue. If you don't have one,
you need to generate one. See the man page for ``ssh-keygen``, and you
may also be interested in ``ssh-agent``. Create it on your personal
computer, and protect the *private* key well -- that includes not
transferring it over the network.

Next, we need to set things up for this newly-created user. The
following command will create a ``~/repositories`` that will hold the
``git`` repositories, a ``~/.gitosis.conf`` that will be a symlink to
the actual configuration file, and it will add the SSH public key to
``~/.ssh/authorized_keys`` with a ``command=`` option that restricts
it to running ``gitosis-serve``. Run::

	sudo -H -u git gitosis-init <FILENAME.pub
	# (or just copy-paste the public key when prompted)

If you want to use ssh-certificates with principals, you need a file with
your admin-user in it. Name it adminuser.txt, only one line with your admins
username in it and run::

        sudo -H -u git gitosis-init <adminuser.txt

then just ``git clone git@SERVER:gitosis-admin.git``, and you get a
repository with SSH keys as ``keys/USER.pub`` and a ``gitosis.conf``
where you can configure who has access to what.

.. warning::

	For now, ``gitosis`` uses the ``HOME`` environment variable to
	locate where to write its files. If you use ``sudo -u``
	without ``-H``, ``sudo`` will leave the old value of ``HOME``
	in place, and this will cause trouble. There will be a
	workaround for that later on, but for now, always remember to
	use ``-H`` if you're sudoing to the account.

You should always edit the configuration file via ``git``. The file
symlinked to ``~/.gitosis.conf`` on the server will be overwritten
when pushing changes to the ``gitosis-admin.git`` repository.

Edit the settings as you wish, commit and push. That's pretty much it!
Once you push, ``gitosis`` will immediately make your changes take
effect on the server.


Managing it
===========

To add new users:

- add a ``keys/USER.pub`` file
- authorize them to read/write repositories as needed (or just
  authorize the group ``@all``)

To create new repositories, just authorize writing to them and
push. It's that simple! For example: let's assume your username is
``jdoe`` and you want to create a repository ``myproject``.
In your clone of ``gitosis-admin``, edit ``gitosis.conf`` and add::

	[group myteam]
	members = jdoe
	writable = myproject

Commit that change and push. Then create the initial commit and push
it::

	mkdir myproject
	cd mypyroject
	git init
	git remote add myserver git@MYSERVER:myproject.git
	# do some work, git add and commit files
	git push myserver master:refs/heads/master

That's it. If you now add others to ``members``, they can use that
repository too.


Example configuration
=====================

.. include:: example.conf
   :literal:


Using ``git daemon``
====================

Anonymous read-only access to ``git`` repositories is provided by
``git daemon``, which is distributed as part of ``git``. But
``gitosis`` will still help you manage it: setting ``daemon = yes`` in
your ``gitosis.conf``, either globally in ``[gitosis]`` or
per-repository under ``[repo REPOSITORYNAME]``, makes ``gitosis``
create the ``git-daemon-export-ok`` files in those repository, thus
telling ``git daemon`` that publishing those repositories is ok.

To actually run ``git daemon`` in Ubuntu, put this in
``/etc/event.d/local-git-daemon``:

.. include:: etc-event.d-local-git-daemon
   :literal:

For other operating systems, use a similar invocation in an ``init.d``
script, ``/etc/inittab``, ``inetd.conf``, ``runit``, or something like
that (good luck).

Note that this short snippet is not a substitute for reading and
understanding the relevant documentation.


Using gitweb
============

``gitweb`` is a CGI script that lets one browse ``git`` repositories
on the web. It is most commonly used anonymously, but you could also
require authentication in your web server, before letting people use
it. ``gitosis`` can help here by generating a list of projects that
are publicly visible. Simply add a section ``[repo REPOSITORYNAME]``
to your ``gitosis.conf``, and allow publishing with ``gitweb = yes``
(or globally under ``[gitosis]``). You should also set ``description``
and ``owner`` for each repository.

Here's a LightTPD_ config file snippet showing how to run ``gitweb``
as a CGI:

.. _LightTPD: http://www.lighttpd.net/

.. include:: lighttpd-gitweb.conf
   :literal:

And a simple ``gitweb.conf`` file:

.. include:: gitweb.conf
   :literal:

Note that this short snippet is not a substitute for reading and
understanding the relevant documentation.


Using ssh-certificates and principals
=====================================

``ssh certificates`` are a new feature of openssh, where you setup your own ssh-CA
and you sign all you host- and user-pubkeys. 

If you want to use certificates ans principals, please visit THIS_ and THIS_ website.
To find out more about the AuthorizedPrincipalCommand in sshd_config, please consult GITLABS_ 
documentation for it.

.. _THIS: https://ef.gy/hardening-ssh
.. _THIS: https://framkant.org/2017/07/scalable-access-control-using-openssh-certificates/
.. _GITLABS: https://docs.gitlab.com/ee/administration/operations/ssh_certificates.html

To use principals and ssh-certificates with this fork of gitosis, please add this snippet to your sshd_config on your git-server::

    Match User git
        AuthorizedPrincipalsCommandUser git
        AuthorizedPrincipalsCommand    /usr/local/bin/gitosis-authorized-principals %i 

And for all users except git, use only principal-files::
    
    Match User !git,*
        AuthorizedPrincipalsFile /etc/ssh/userprincipals/%u


This will run the command as user "git", which will you have installed, when you serve your gitrepos with gitosis. 
%i is the key-identity of your certificate, which will you give on your sign-process to the user-certificate.

Then you need an additional line in your gitosis.conf in the [gitosis]-section::

    [gitosis]
    ...
    allowedPrincipals = git gitosis-admin

In the members-line of your gitosis.conf, you have to write down the key-identity (which is passed as %i in you sshd_config). If you are not sure,
what the identity is, try::

    ssh-keygen -L -f ~/.ssh/id_rsa-cert.pub

    /home/myusername/.ssh/id_rsa-cert.pub:
        Type: ssh-rsa-cert-v01@openssh.com user certificate
        Public key: RSA-CERT SHA256:cjLH4l45G32zOaJBjv8Udnr7bkwHRNB3nAz0a6SCOl0
        Signing CA: ED25519 SHA256:9bMENs+blen§naslr§BJEN421I5ckbu4mvpnktiHdUs (using ssh-ed25519)
        Key ID: "myusername"
        Serial: 4
        Valid: from 2019-08-02T02:29:00 to 2020-08-01T02:30:20
        Principals: 
                myusername
                principal2
                git
                gitosis-admin
        Critical Options: (none)
        Extensions: 
                permit-X11-forwarding
                permit-agent-forwarding
                permit-port-forwarding
                permit-pty
                permit-user-rc

from your principals in the key, only git and gitosis-admin are allowed. You must have at least one of this allowed principals in your key, to get access to your gitosis-served repos.
Access is only given, if you have one of the allowed principals in your certificate, and your key ID is listed as member in the repo

Parallel use of principals/certificates an pubkeys
--------------------------------------------------

It is possible, to use pubkeys in parallel to these principals from certificates. Just as described above. If you have a user, which has no certificate from your ssh-CA, just add his
public-sshkey in the keydir. (not tested now)


Contact
=======

You can email the author at ``tv@eagain.net``, or hop on
``irc.freenode.net`` channel ``#git`` and hope for the best.

For ssh-certificates and principals, please contact wertstoffe@xundeenergie.at

There will be more, keep an eye on http://eagain.net/ and/or the git
mailing list.
