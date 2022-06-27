SERVICE=	nsd
ZONE=		.


build:
	docker-compose build

up:
	docker-compose create
	$(MAKE) config
	docker-compose start

down:
	docker-compose down
		
cli:
	docker-compose exec $(SERVICE) bash

axfr:
	docker-compose exec $(SERVICE) dig @127.0.0.1 -p 5303 $(ZONE) axfr

reconfig: config
	docker-compose exec $(SERVICE) nsd-checkconf /config/nsd.conf
	docker-compose exec $(SERVICE) nsd-control reload

config:
	docker-compose cp nsd.conf $(SERVICE):/config/nsd.conf

realclean:
	docker volume rm nsd_config nsd_storage
