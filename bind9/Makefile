COMPOSE=	docker-compose
SERVICE=	bind9


build:
	$(COMPOSE) build

up:
	$(COMPOSE) create
	$(MAKE) config
	$(COMPOSE) start

down:
	$(COMPOSE) down
		
cli:
	$(COMPOSE) exec $(SERVICE) bash

axfr:
	$(COMPOSE) exec $(SERVICE) dig @127.0.0.1 -p 5302 example.com axfr

reconfig: config
	$(COMPOSE) exec $(SERVICE) rndc reconfig

config:
	$(COMPOSE) cp named.conf $(SERVICE):/config/named.conf
	$(COMPOSE) cp example.com.zone $(SERVICE):/storage/example.com.zone

realclean:
	docker volume rm bind9_config bind9_storage bind9_softhsm
