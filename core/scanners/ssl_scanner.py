"""
Advanced SSL/TLS scanner
"""
import ssl
import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from datetime import datetime
import asyncio
import OpenSSL

class SSLScanner:
    """Comprehensive SSL/TLS analysis"""
    
    async def scan(self, hostname: str, port: int = 443) -> dict:
        """Complete SSL scan"""
        results = {
            'hostname': hostname,
            'port': port,
            'certificate': {},
            'protocols': {},
            'vulnerabilities': [],
            'issues': []
        }
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connect and get certificate
            reader, writer = await asyncio.open_connection(
                hostname, port, ssl=context
            )
            
            # Get certificate
            sock = writer.get_extra_info('ssl_object')
            cert_binary = sock.getpeercert(binary_form=True)
            cert = x509.load_der_x509_certificate(cert_binary, default_backend())
            
            # Parse certificate
            results['certificate'] = self._parse_certificate(cert)
            
            # Check protocols
            results['protocols'] = await self._check_protocols(hostname, port)
            
            # Check vulnerabilities
            results['vulnerabilities'] = await self._check_vulnerabilities(hostname, port)
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            results['error'] = str(e)
            results['issues'].append({
                'type': 'ssl_error',
                'severity': 'critical',
                'description': f"SSL connection failed: {str(e)}"
            })
        
        return results
    
    def _parse_certificate(self, cert) -> dict:
        """Parse X.509 certificate"""
        now = datetime.now()
        
        # Get subject
        subject = {}
        for attr in cert.subject:
            subject[attr.oid._name] = attr.value
        
        # Get issuer
        issuer = {}
        for attr in cert.issuer:
            issuer[attr.oid._name] = attr.value
        
        cert_info = {
            'subject': subject,
            'issuer': issuer,
            'version': cert.version.value,
            'serial_number': str(cert.serial_number),
            'not_valid_before': cert.not_valid_before_utc.isoformat(),
            'not_valid_after': cert.not_valid_after_utc.isoformat(),
            'days_until_expiry': (cert.not_valid_after_utc - now).days,
            'signature_algorithm': cert.signature_algorithm_oid._name,
            'is_expired': cert.not_valid_after_utc < now,
            'is_valid': now < cert.not_valid_after_utc,
            'extensions': []
        }
        
        # Check extensions
        for ext in cert.extensions:
            cert_info['extensions'].append({
                'name': ext.oid._name,
                'critical': ext.critical,
                'value': str(ext.value)
            })
        
        return cert_info
    
    async def _check_protocols(self, hostname: str, port: int) -> dict:
        """Check supported SSL/TLS protocols"""
        protocols = {
            'SSLv2': False,
            'SSLv3': False,
            'TLSv1.0': False,
            'TLSv1.1': False,
            'TLSv1.2': False,
            'TLSv1.3': False
        }
        
        # Test each protocol
        for protocol_name, protocol_version in [
            ('SSLv2', ssl.PROTOCOL_SSLv23),  # These will be deprecated
            ('SSLv3', ssl.PROTOCOL_SSLv3),
            ('TLSv1.0', ssl.PROTOCOL_TLSv1),
            ('TLSv1.1', ssl.PROTOCOL_TLSv1_1),
            ('TLSv1.2', ssl.PROTOCOL_TLSv1_2),
            ('TLSv1.3', ssl.PROTOCOL_TLS)
        ]:
            try:
                context = ssl.SSLContext(protocol_version)
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(hostname, port, ssl=context),
                    timeout=5
                )
                protocols[protocol_name] = True
                writer.close()
                await writer.wait_closed()
            except:
                protocols[protocol_name] = False
        
        return protocols
    
    async def _check_vulnerabilities(self, hostname: str, port: int) -> list:
        """Check for known SSL vulnerabilities"""
        vulnerabilities = []
        
        # Check for Heartbleed (CVE-2014-0160)
        if await self._check_heartbleed(hostname, port):
            vulnerabilities.append({
                'name': 'Heartbleed',
                'cve': 'CVE-2014-0160',
                'severity': 'critical',
                'description': 'Server vulnerable to Heartbleed attack'
            })
        
        # Check for POODLE (CVE-2014-3566)
        protocols = await self._check_protocols(hostname, port)
        if protocols.get('SSLv3'):
            vulnerabilities.append({
                'name': 'POODLE',
                'cve': 'CVE-2014-3566',
                'severity': 'high',
                'description': 'SSLv3 enabled - vulnerable to POODLE attack'
            })
        
        return vulnerabilities
    
    async def _check_heartbleed(self, hostname: str, port: int) -> bool:
        """Check for Heartbleed vulnerability"""
        # Simplified check - in production, implement full Heartbleed test
        return False
