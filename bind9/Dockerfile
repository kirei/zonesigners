FROM debian:stable

ENV OPENSSL_CONF=/etc/bind/openssl.cnf

VOLUME /storage
VOLUME /config

RUN apt-get update
RUN apt-get install -y procps sudo softhsm gnutls-bin
RUN apt-get install -y openssl libengine-pkcs11-openssl
RUN apt-get install -y bind9 bind9-dnsutils
RUN apt-get install -y opensc

RUN install -d -m 750 -o bind -g bind /run/named
RUN usermod -G softhsm bind

ADD entrypoint.sh /
ADD openssl.cnf /etc/bind

ENTRYPOINT bash /entrypoint.sh
