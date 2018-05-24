#!/bin/bash

unset DEBCONF_REDIR
unset DEBCONF_FRONTEND
unset DEBIAN_HAS_FRONTEND
unset DEBIAN_FRONTEND

bash /root/scripts/postinstall.sh
rm -rf /root/scripts
