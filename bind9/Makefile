SERVICE=	bind9


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
	docker-compose exec $(SERVICE) dig @127.0.0.1 -p 5302 example.com axfr

reconfig: config
	docker-compose exec $(SERVICE) rndc reconfig

config:
	docker-compose cp named.conf $(SERVICE):/config/named.conf
	docker-compose cp example.com.zone $(SERVICE):/storage/example.com.zone

realclean:
	docker volume rm bind9_config bind9_storage bind9_softhsm
