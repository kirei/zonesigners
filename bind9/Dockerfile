FROM fedora:latest

VOLUME /storage
VOLUME /config

RUN dnf -y update
RUN dnf -y install bind gnutls-utils softhsm

ADD entrypoint.sh /

ENTRYPOINT bash /entrypoint.sh
