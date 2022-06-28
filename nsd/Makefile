COMPOSE=	docker-compose
SERVICE=	nsd


build:
	$(COMPOSE) build

up:
	(cd zones; make)
	$(COMPOSE) create
	$(MAKE) config
	$(COMPOSE) start

down:
	$(COMPOSE) down
		
cli:
	$(COMPOSE) exec $(SERVICE) bash

axfr:
	$(COMPOSE) exec $(SERVICE) dig @127.0.0.1 -p 5303 signed.example.com axfr

reconfig: config
	$(COMPOSE) exec $(SERVICE) nsd-checkconf /config/nsd.conf
	$(COMPOSE) exec $(SERVICE) nsd-control reload

config:
	$(COMPOSE) cp nsd.conf $(SERVICE):/config/nsd.conf
	$(COMPOSE) cp nsd2.conf $(SERVICE):/config/nsd2.conf
	$(COMPOSE) cp zones/unsigned.example.com.zone $(SERVICE):/storage/unsigned.example.com
	$(COMPOSE) cp zones/signed.example.com.zone.signed $(SERVICE):/storage/signed.example.com
	$(COMPOSE) cp zones/broken.example.com.zone.signed $(SERVICE):/storage/broken.example.com

clean:
	(cd zones; make clean)

realclean: clean
	docker volume rm nsd_config nsd_storage
