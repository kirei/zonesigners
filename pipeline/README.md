# Example Zone Pipeline

## Components

### Registry

Address: 10.0.0.11

- Load zone from disk
- Create ZONEMD RR
- Provide zone transfer to authority

### Authority

Address: 10.0.0.12

- Transfer zone from registry
- Provide zone transfer to ingress

### Ingress

Address: 10.0.0.13

- Transfer zone from authority
- Check syntax
- Provide zone transfer to signer

### Signer

Address: 10.0.0.14

- Transfer zone from ingress
- Sign zone
- Provide zone transfer to egress

### Egress

Address: 10.0.0.15

- Transfer zone from signer
- Check syntax
- Provide zone transfer



## Software

- [Knot](https://www.knot-dns.cz/)
- [NSD](https://nsd.docs.nlnetlabs.nl/en/latest/)


## Container Images

- [Knot](https://hub.docker.com/r/cznic/knot)
- [NSD](https://hub.docker.com/r/jschlyter/nsd)
