FROM cznic/knot:latest

RUN apt-get update
RUN apt-get install -y procps sudo softhsm

RUN usermod -G softhsm knot

ADD entrypoint.sh /

ENTRYPOINT bash /entrypoint.sh
