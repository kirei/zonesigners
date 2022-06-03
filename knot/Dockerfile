FROM cznic/knot:latest

RUN apt-get update
RUN apt-get install -y procps sudo softhsm

ADD entrypoint.sh /

ENTRYPOINT bash /entrypoint.sh
