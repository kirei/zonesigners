#!/bin/bash

usermod -G softhsm knot

if [ ! -f /var/lib/softhsm/.initialized ]; then
	sudo -u knot softhsm2-util --init-token --free --label knot --pin 1234 --so-pin 1234567890
	touch /var/lib/softhsm/.initialized
fi

knotd --verbose
