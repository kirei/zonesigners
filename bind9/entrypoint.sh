#!/bin/bash

usermod -G softhsm named

if [ ! -f /var/lib/softhsm/.initialized ]; then
	sudo -u named softhsm2-util --init-token --free --label named --pin 1234 --so-pin 1234567890
	touch /var/lib/softhsm/.initialized
fi

if [ ! -f /etc/rndc.key ]; then
	rndc-confgen -a
	chown named /etc/rndc.key
	chmod g+r /etc/rndc.key
fi

if [ ! -d /storage/keys ]; then
	install -d -g named -m 770 /storage/keys
fi

#named -E pkcs11 -g
named -g -c /config/named.conf
