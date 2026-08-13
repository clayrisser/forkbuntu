#!/bin/sh

unset DEBCONF_REDIR
unset DEBCONF_FRONTEND
unset DEBIAN_HAS_FRONTEND
unset DEBIAN_FRONTEND

sh /root/scripts/postinstall.sh
rm -rf /root/scripts
