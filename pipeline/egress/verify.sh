#!/bin/bash

ORIGIN=${1:-.}
ZONEFILE=/tmp/${ORIGIN}.zone

rm -f $ZONEFILE
cat > $ZONEFILE

echo Running ldns-verify-zone
ldns-verify-zone -V 5 -ZZ < $ZONEFILE
if [ $? -ne 0 ]; then
	echo "ldns-verify-zone failed"
	exit 1
else
	echo "ldns-verify-zone succeeded"
fi

echo Running kzonecheck
kzonecheck --origin $ORIGIN --dnssec on --verbose $ZONEFILE
if [ $? -ne 0 ]; then
	echo "kzonecheck failed"
	exit 2
else
	echo "kzonecheck succeeded"
fi

echo Running kzonecheck
dnssec-verify -o $ORIGIN -x $ZONEFILE
if [ $? -ne 0 ]; then
	echo "dnssec-verify failed"
	exit 3
else
	echo "dnssec-verify succeeded"
fi

echo "zone verified successfully"
exit 0
