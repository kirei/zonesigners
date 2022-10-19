FROM jschlyter/nsd:latest

ENV EXTRA_PKGS \
	ldnsutils \
	knot-dnssecutils \
	bind9

RUN apt-get update && apt-get install -yqq ${EXTRA_PKGS}
