#!/bin/sh

if [ -n "$DISPLAY" -a -f /usr/sbin/system-config-network-gui ]; then
    exec /usr/sbin/system-config-network-gui "$@"
else
    exec /usr/sbin/system-config-network-tui "$@"
fi
