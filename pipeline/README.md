# Example Zone Pipeline

## Components

### Registry

- Load zone from disk
- Create ZONEMD RR
- Provide zone transfer to authority

### Authority

- Transfer zone from registry
- Provide zone transfer to ingress

### Ingress

- Transfer zone from authority
- Check syntax
- Provide zone transfer to signer

### Signer

- Transfer zone from ingress
- Sign zone
- Provide zone transfer to egress

### Egress

- Transfer zone from signer
- Check syntax
- Provide zone transfer
