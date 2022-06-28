all: clean keygen sign


keygen:
	dnssec-keygen -a ECDSAP256SHA256 -f KSK signed.example.com
	dnssec-keygen -a ECDSAP256SHA256        signed.example.com
	dnssec-keygen -a ECDSAP256SHA256 -f KSK broken.example.com
	dnssec-keygen -a ECDSAP256SHA256        broken.example.com

sign:
	dnssec-signzone -S -o signed.example.com signed.example.com.zone
	dnssec-signzone -S -o broken.example.com -f not-yet-broken.tmp broken.example.com.zone
	sed "s/mail/nail/g" < not-yet-broken.tmp > broken.example.com.zone.signed
	rm -f not-yet-broken.tmp
	dnssec-verify -o signed.example.com signed.example.com.zone.signed
	-dnssec-verify -o broken.example.com broken.example.com.zone.signed

clean:
	rm -f K*.key K*.private dsset-*
	rm -f *.signed *.tmp
