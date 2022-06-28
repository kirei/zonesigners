COMPOSE=	docker-compose
SERVICE=	knot


build:
	$(COMPOSE) build

up:
	$(COMPOSE) create
	$(MAKE) config
	$(COMPOSE) start
	$(MAKE) keygen

down:
	$(COMPOSE) down
		
cli:
	$(COMPOSE) exec $(SERVICE) bash

axfr:
	$(COMPOSE) exec $(SERVICE) kdig @127.0.0.1 -p 5301 example.com axfr

keygen:
	$(COMPOSE) exec $(SERVICE) sudo -u knot keymgr example.com generate ksk=true
	$(COMPOSE) exec $(SERVICE) sudo -u knot keymgr example.com generate ksk=false
	$(COMPOSE) exec $(SERVICE) knotc reload

pregenerate:
	$(COMPOSE) exec $(SERVICE) sudo -u knot keymgr example.com pregenerate +365d

reconfig: config
	$(COMPOSE) exec $(SERVICE) knotc conf-check
	$(COMPOSE) exec $(SERVICE) knotc reload

config:
	$(COMPOSE) cp knot.conf $(SERVICE):/config/knot.conf
	$(COMPOSE) cp example.com.zone $(SERVICE):/storage/example.com.zone

realclean:
	docker volume rm knot_config knot_storage knot_softhsm
