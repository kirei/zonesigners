SERVICE=	nsd


build:
	docker-compose build

up:
	(cd zones; make)
	docker-compose create
	$(MAKE) config
	docker-compose start

down:
	docker-compose down
		
cli:
	docker-compose exec $(SERVICE) bash

axfr:
	docker-compose exec $(SERVICE) dig @127.0.0.1 -p 5303 signed.example.com axfr

reconfig: config
	docker-compose exec $(SERVICE) nsd-checkconf /config/nsd.conf
	docker-compose exec $(SERVICE) nsd-control reload

config:
	docker-compose cp nsd.conf $(SERVICE):/config/nsd.conf
	docker-compose cp nsd2.conf $(SERVICE):/config/nsd2.conf
	docker-compose cp zones/unsigned.example.com.zone $(SERVICE):/storage/unsigned.example.com
	docker-compose cp zones/signed.example.com.zone.signed $(SERVICE):/storage/signed.example.com
	docker-compose cp zones/broken.example.com.zone.signed $(SERVICE):/storage/broken.example.com

clean:
	(cd zones; make clean)

realclean: clean
	docker volume rm nsd_config nsd_storage
