#!/bin/bash

ORIGIN=${1:-.}
ZONEFILE=/tmp/${ORIGIN}.zone

rm -f $ZONEFILE
cat > $ZONEFILE

ldns-verify-zone -V 5 < $ZONEFILE && \
kzonecheck --origin $ORIGIN --dnssec on --verbose $ZONEFILE && \
dnssec-verify -o $ORIGIN -x $ZONEFILE

ret=$?

exit $res
