SERVICE=	knot


build:
	docker-compose build

up:
	docker-compose create
	$(MAKE) config
	docker-compose start
	$(MAKE) keygen

down:
	docker-compose down
		
cli:
	docker-compose exec $(SERVICE) bash

axfr:
	docker-compose exec $(SERVICE) kdig @127.0.0.1 -p 5301 example.com axfr

keygen:
	docker-compose exec $(SERVICE) sudo -u knot keymgr example.com generate ksk=true
	docker-compose exec $(SERVICE) sudo -u knot keymgr example.com generate ksk=false
	docker-compose exec $(SERVICE) knotc reload

pregenerate:
	docker-compose exec $(SERVICE) sudo -u knot keymgr example.com pregenerate +365d

reconfig: config
	docker-compose exec $(SERVICE) knotc conf-check
	docker-compose exec $(SERVICE) knotc reload

config:
	docker-compose cp knot.conf $(SERVICE):/config/knot.conf
	docker-compose cp example.com.zone $(SERVICE):/storage/example.com.zone

realclean:
	docker volume rm knot_config knot_storage knot_softhsm
