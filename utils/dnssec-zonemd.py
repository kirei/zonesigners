"""
Check DNSSEC signer using ZONEMD:

1. read unsigned zone information from file or via DNS query
2. read signed zone from file 
3. calculate ZONEMD from signed zone data after stripping all DNSSEC RRs
   (using SOA serial from the unsigned zone)
4. ensure calculated ZONEMD matches unsigned ZONEMD
"""

import argparse
import logging
from dataclasses import dataclass

import dns.message
import dns.query
import dns.rdataset
import dns.rdatatype
import dns.zone
from dns.zonetypes import DigestHashAlgorithm

DNSSEC_RDATATYPES = {
    dns.rdatatype.DNSKEY,
    dns.rdatatype.RRSIG,
    dns.rdatatype.NSEC,
    dns.rdatatype.NSEC3,
    dns.rdatatype.NSEC3PARAM,
}


@dataclass(frozen=True)
class ZoneInformation:
    soa_rds: dns.rdataset.Rdataset
    zonemd_rds: dns.rdataset.Rdataset

    @classmethod
    def from_file(cls, origin: str, filename: str):
        zone = dns.zone.from_file(
            filename, check_origin=False, relativize=False, origin=origin
        )

        soa_rds = zone.get_rdataset("@", dns.rdatatype.SOA)
        zonemd_rds = zone.get_rdataset("@", dns.rdatatype.ZONEMD)

        # if we don't have a ZONEMD in the file already, calculate one
        if zonemd_rds is None:
            zonemd_rrset = zone.compute_digest(DigestHashAlgorithm.SHA384)
            zonemd_rds = dns.rdataset.from_rdata_list(soa_rds.ttl, [zonemd_rrset])

        return cls(soa_rds=soa_rds, zonemd_rds=zonemd_rds)

    @classmethod
    def from_dns(cls, origin: str, server: str):
        qname = dns.name.from_text(origin)

        # query for SOA
        q = dns.message.make_query(qname, dns.rdatatype.SOA)
        response = dns.query.udp(q, server)
        soa_rds = dns.rdataset.from_rdata_list(
            response.answer[0].ttl, response.answer[0]
        )

        # query for ZONEMD
        q = dns.message.make_query(qname, dns.rdatatype.ZONEMD)
        response = dns.query.udp(q, server)
        zonemd_rds = dns.rdataset.from_rdata_list(soa_rds.ttl, response.answer[0])

        return cls(soa_rds=soa_rds, zonemd_rds=zonemd_rds)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", dest="debug", action="store_true", help="Enable debugging"
    )
    parser.add_argument(
        "--origin", "-o", type=str, default=".", help="zone origin", required=True
    )
    parser.add_argument(
        "--unsigned-zone", dest="unsigned_zonefile", type=str, help="Unsigned zone file"
    )
    parser.add_argument(
        "--unsigned-server",
        dest="unsigned_server",
        type=str,
        help="Unsigned name server",
    )
    parser.add_argument(
        "--signed-zone",
        dest="signed_zonefile",
        type=str,
        help="Signed zone file",
        required=True,
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.unsigned_zonefile:
        unsigned = ZoneInformation.from_file(args.origin, args.unsigned_zonefile)
    elif args.unsigned_server:
        unsigned = ZoneInformation.from_dns(args.origin, args.unsigned_server)
    else:
        raise ValueError("No unsigned zone source")

    logging.info("ZONEMD unsigned: %s", unsigned.zonemd_rds[0])

    signed_zone = dns.zone.from_file(
        args.signed_zonefile, check_origin=False, relativize=False, origin=args.origin
    )
    signed_zone.verify_digest()

    signed_zonemd_rds = signed_zone.get_rdataset("@", dns.rdatatype.ZONEMD)
    logging.debug("ZONEMD signed (original): %s", signed_zonemd_rds[0])

    stripped_zone = signed_zone
    stripped_rds = []

    for (name, node) in stripped_zone.items():
        for rds in node:
            if rds.rdtype in DNSSEC_RDATATYPES:
                stripped_rds.append((name, rds))

    for name, rds in stripped_rds:
        stripped_zone.delete_rdataset(name, rds.rdtype, rds.covers)

    # replace SOA with unsigned version
    stripped_zone.replace_rdataset("@", unsigned.soa_rds)
    stripped_zonemd = stripped_zone.compute_digest(
        unsigned.zonemd_rds[0].hash_algorithm
    )

    logging.info("ZONEMD signed (stripped): %s", stripped_zonemd)

    if stripped_zonemd != unsigned.zonemd_rds[0]:
        raise ValueError("ZONEMD mismatch, signed zone changed")


if __name__ == "__main__":
    main()
