#!/bin/bash

if [ ! -f /var/lib/softhsm/.initialized ]; then
	sudo -u bind softhsm2-util --init-token --free --label named --pin 1234 --so-pin 1234567890
	touch /var/lib/softhsm/.initialized
fi

if [ ! -d /storage/keys ]; then
	install -d -g bind -m 770 /storage/keys
	sudo -u bind pkcs11-tool \
		--module /usr/lib/softhsm/libsofthsm2.so \
		--login --token-label named --pin 1234 \
		--keypairgen --key-type EC:prime256v1 --label ksk1 
	sudo -u bind pkcs11-tool \
		--module /usr/lib/softhsm/libsofthsm2.so \
		--login --token-label named --pin 1234 \
		--keypairgen --key-type EC:prime256v1 --label zsk1 
	sudo -u bind dnssec-keyfromlabel -E pkcs11 -K /storage/keys \
		-a ECDSAP256SHA256 \
		-l "token=named;object=ksk1;pin-value=1234" \
		-f KSK \
		example.com
	sudo -u bind dnssec-keyfromlabel -E pkcs11 -K /storage/keys \
		-a ECDSAP256SHA256 \
		-l "token=named;object=ksk1;pin-value=1234" \
		example.com
fi

chown bind:bind /config
chown bind:bind /storage

named -E pkcs11 -u bind -g -c /config/named.conf
