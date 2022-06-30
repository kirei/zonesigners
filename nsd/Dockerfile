FROM debian:stable AS builder

RUN apt-get -y update
RUN apt-get -y install build-essential
RUN apt-get -y install git autoconf libevent-dev libssl-dev bison flex curl

WORKDIR /src

#RUN git clone https://github.com/NLnetLabs/nsd /src
RUN curl -L https://github.com/NLnetLabs/nsd/archive/refs/tags/NSD_4_6_0_REL.tar.gz | tar --strip-components 1 -xzf -

RUN aclocal && autoconf && autoheader
RUN ./configure --with-configdir=/config --localstatedir=/storage --enable-root-server
RUN make
RUN make DESTDIR=/tmp/nsd install
RUN tar cvzfC /nsd.tar.gz /tmp/nsd usr/local config storage


FROM debian:stable

RUN apt-get -y update
RUN apt-get -y install procps ldnsutils openssl libssl1.1 libevent-2.1
RUN apt-get -y install bind9-dnsutils

COPY --from=builder /nsd.tar.gz /tmp
RUN tar xvzpf /tmp/nsd.tar.gz
RUN rm -f /tmp/nsd.tar.gz

RUN groupadd nsd
RUN useradd -r -m -g nsd nsd

ADD entrypoint.sh /

ENTRYPOINT bash /entrypoint.sh
