# Zone Signers Testbed

This repository contains container-based test configurations for signing zones with BIND 9 and Knot using a PKCS#11 provider.

- To build each container, use: `make build`
- To start the signer, use `make up` 

There are also targets for starting a CLI session in the container, do an AXFR of the signed zone as well as shutting down the environment.
