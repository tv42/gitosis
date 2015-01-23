#!/bin/bash

# This is just an example how to backup all repositorie under $HOME/repositories
# to other host. This should be run as a git user. You should allow git user
# to access git@backup-host and allow git@backup-host to access your repositories.
# (ie. you should add public key git@backup-host.pub to gitosis-admin/keydir and
# add to gitosis.conf something like this:
#   [group buckap]
#   members = git@backup-host
#   readable = *
# )

backup_service=git@backup-host

pushd $HOME/repositories
for repo in *.git;
do
	if ssh git@backup-host test -e repositories/$repo;
	then
		cd repositories/$repo
		git push --mirror git@backup-host:repositories/$repo
	else
		ssh git@backup-host git clone --mirror git@atlantis:$repo repositories/$repo 
	fi
done
popd
