DOCKER=		docker
COMPOSE=	docker-compose

PREFIX=		pipeline_
ZONE=		example.com
VOLUMES=	$(PREFIX)registry_config \
		$(PREFIX)registry_storage \
		$(PREFIX)authority_config \
		$(PREFIX)authority_storage \
		$(PREFIX)ingress_config \
		$(PREFIX)ingress_storage \
		$(PREFIX)signer_config \
		$(PREFIX)signer_storage \
		$(PREFIX)egress_config \
		$(PREFIX)egress_storage


all:

build:
	$(COMPOSE) build

up:
	$(COMPOSE) create
	$(MAKE) config
	$(COMPOSE) start
	$(MAKE) retransfer

down:
	$(COMPOSE) down
		
cli:
	$(COMPOSE) exec $(SERVICE) bash

axfr:
	@echo "### Checking registry"
	$(COMPOSE) exec registry kdig @10.0.0.11 $(ZONE) axfr
	@echo "### Checking authority"
	$(COMPOSE) exec authority kdig @10.0.0.12 $(ZONE) axfr
	@echo "### Checking ingress"
	$(COMPOSE) exec signer kdig @10.0.0.13 $(ZONE) axfr
	@echo "### Checking signer"
	$(COMPOSE) exec signer kdig @10.0.0.14 $(ZONE) axfr
	@echo "### Checking egress"
	$(COMPOSE) exec signer kdig @10.0.0.15 $(ZONE) axfr

reload:
	$(COMPOSE) exec registry knotc zone-reload $(ZONE)

resign:
	$(COMPOSE) exec signer knotc zone-sign $(ZONE)

reconfig:
	$(COMPOSE) exec registry knotc reload
	$(COMPOSE) exec authority knotc reload
	$(COMPOSE) exec ingress nsd-control reconfig
	$(COMPOSE) exec signer knotc reload
	$(COMPOSE) exec egress nsd-control reconfig

retransfer:
	$(COMPOSE) exec authority knotc zone-retransfer $(ZONE)
	$(COMPOSE) exec ingress nsd-control force_transfer $(ZONE)
	$(COMPOSE) exec signer knotc zone-retransfer $(ZONE)
	$(COMPOSE) exec egress nsd-control force_transfer $(ZONE)

config:
	$(COMPOSE) cp registry/$(ZONE).zone registry:/storage/$(ZONE).zone
	$(COMPOSE) cp registry/knot.conf registry:/config/knot.conf
	$(COMPOSE) cp authority/knot.conf authority:/config/knot.conf
	$(COMPOSE) cp ingress/nsd.conf ingress:/config/nsd.conf
	$(COMPOSE) cp signer/knot.conf signer:/config/knot.conf
	$(COMPOSE) cp egress/nsd.conf egress:/config/nsd.conf
	$(COMPOSE) cp egress/verify.sh egress:/config/verify.sh

realclean:
	$(DOCKER) volume rm -f $(VOLUMES)
