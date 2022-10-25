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
import sys
import time
from dataclasses import dataclass
from typing import Optional

import dns.message
import dns.query
import dns.rdataset
import dns.rdatatype
import dns.zone

DNSSEC_RDATATYPES = {
    dns.rdatatype.CDNSKEY,
    dns.rdatatype.CDS,
    dns.rdatatype.DNSKEY,
    dns.rdatatype.NSEC,
    dns.rdatatype.NSEC3,
    dns.rdatatype.NSEC3PARAM,
    dns.rdatatype.RRSIG,
}

DEFAULT_DIGEST_HASH_ALGORITHM = dns.zone.DigestHashAlgorithm.SHA384


class measure_elapsed_time(object):
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start


@dataclass(frozen=True)
class ZoneInformation:
    soa_rds: dns.rdataset.Rdataset
    zonemd_rds: Optional[dns.rdataset.Rdataset]

    @property
    def zonemd(self):
        return self.zonemd_rds[0] if self.zonemd_rds else None

    @classmethod
    def from_file(cls, origin: str, filename: str):
        zone = dns.zone.from_file(
            filename, check_origin=False, relativize=False, origin=origin
        )

        soa_rds = zone.get_rdataset("@", dns.rdatatype.SOA)
        zonemd_rds = zone.get_rdataset("@", dns.rdatatype.ZONEMD)

        # if we don't have a ZONEMD in the file already, calculate one
        if zonemd_rds is None:
            zonemd_rrset = zone.compute_digest(DEFAULT_DIGEST_HASH_ALGORITHM)
            zonemd_rds = dns.rdataset.from_rdata_list(soa_rds.ttl, [zonemd_rrset])

        return cls(soa_rds=soa_rds, zonemd_rds=zonemd_rds)

    @classmethod
    def from_dns(cls, origin: str, server: str, port: int = 53):
        qname = dns.name.from_text(origin)

        # query for SOA
        q = dns.message.make_query(qname, dns.rdatatype.SOA)
        response = dns.query.udp(q, server)
        soa_rds = dns.rdataset.from_rdata_list(
            response.answer[0].ttl, response.answer[0]
        )

        # query for ZONEMD
        q = dns.message.make_query(qname, dns.rdatatype.ZONEMD)
        response = dns.query.udp(q, where=server, port=port)
        if len(response.answer):
            zonemd_rds = dns.rdataset.from_rdata_list(soa_rds.ttl, response.answer[0])
        else:
            zonemd_rds = None

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
        help="Unsigned name server address",
    )
    parser.add_argument(
        "--unsigned-port",
        dest="unsigned_port",
        type=int,
        default=53,
        help="Unsigned name server port",
    )
    parser.add_argument(
        "--signed-zone",
        dest="signed_zonefile",
        type=str,
        help="Signed zone file",
    )
    parser.add_argument(
        "--signed-server",
        dest="signed_server",
        type=str,
        help="Signed name server address",
    )
    parser.add_argument(
        "--signed-port",
        dest="signed_port",
        type=int,
        default=53,
        help="Signed name server port",
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    t = time.perf_counter()

    with measure_elapsed_time() as t:
        if args.unsigned_zonefile:
            unsigned = ZoneInformation.from_file(args.origin, args.unsigned_zonefile)
        elif args.unsigned_server:
            unsigned = ZoneInformation.from_dns(args.origin, args.unsigned_server, args.unsigned_port)
        else:
            raise ValueError("No unsigned zone source")
    logging.debug("Processed unsigned zone in %.3f seconds", t.elapsed)

    if unsigned.zonemd:
        logging.info("ZONEMD unsigned: %s", unsigned.zonemd)
    else:
        logging.error("No ZONEMD in unsigned zone")
        sys.exit(-2)

    with measure_elapsed_time() as t:
        if args.signed_zonefile:
            signed_zone = dns.zone.from_file(
                args.signed_zonefile,
                check_origin=False,
                relativize=False,
                origin=args.origin,
            )
        elif args.signed_server:
            signed_zone = dns.zone.from_xfr(
                dns.query.xfr(zone=args.origin, where=args.signed_server, port=args.signed_port)
            )
        else:
            raise ValueError("No signed zone source")
    logging.debug("Read signed zone in %.3f seconds", t.elapsed)

    with measure_elapsed_time() as t:
        try:
            signed_zone.verify_digest()
        except dns.zone.NoDigest:
            logging.error("No ZONEMD in signed zone")
            sys.exit(-2)
    logging.debug("Verified zone in %.3f seconds", t.elapsed)

    signed_zonemd_rds = signed_zone.get_rdataset("@", dns.rdatatype.ZONEMD)
    signed_zonemd = signed_zonemd_rds[0]
    logging.info("ZONEMD signed: %s", signed_zonemd)

    stripped_zone = signed_zone
    stripped_rds = []

    with measure_elapsed_time() as t:
        for (name, node) in stripped_zone.items():
            for rds in node:
                if rds.rdtype in DNSSEC_RDATATYPES:
                    stripped_rds.append((name, rds))
    logging.debug("Searched zone in %.3f seconds", t.elapsed)

    with measure_elapsed_time() as t:
        for name, rds in stripped_rds:
            stripped_zone.delete_rdataset(name, rds.rdtype, rds.covers)
    logging.debug("Stripped zone of all DNSSEC RRs in %.3f seconds", t.elapsed)

    # replace SOA with unsigned version and calculate ZONEMD
    with measure_elapsed_time() as t:
        stripped_zone.replace_rdataset("@", unsigned.soa_rds)
        stripped_zonemd = stripped_zone.compute_digest(
            unsigned.zonemd.hash_algorithm
            if unsigned.zonemd
            else DEFAULT_DIGEST_HASH_ALGORITHM
        )
    logging.debug("Computed new ZONEMD in %.3f seconds", t.elapsed)

    logging.info("ZONEMD stripped: %s", stripped_zonemd)
    if stripped_zonemd != unsigned.zonemd:
        logging.error("ZONEMD mismatch, signed zone altered")
        sys.exit(-1)


if __name__ == "__main__":
    main()
