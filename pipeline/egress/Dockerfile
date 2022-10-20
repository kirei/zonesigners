FROM jschlyter/nsd:latest

ENV EXTRA_PKGS \
	ldnsutils \
	knot-dnssecutils \
	bind9 \
	python3-dnspython

RUN apt-get update && apt-get install -yqq ${EXTRA_PKGS}

ADD https://raw.githubusercontent.com/kirei/zonesigners/main/utils/dnssec-zonemd.py /usr/local/src/dnssec-zonemd.py
RUN chmod 444 /usr/local/src/dnssec-zonemd.py
