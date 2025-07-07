from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta

from database.database import SessionLocal
from entity.ca import Ca
from entity.company import Company


def generate_entreprise_pki(name):
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    # 2. Créer certificat auto-signé (CA)
    ca_name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, f"{name}"),
    ])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )


    company_ca = Ca()
    session = SessionLocal()
    public_key = ca_cert.public_bytes(serialization.Encoding.PEM)
    private_key = ca_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption())
    expiration_date = ca_cert.not_valid_after_utc
    company_ca.add_new_pki(session, private_key, public_key, expiration_date)


def generate_agent_pki(company_id, agent_name):
    session = SessionLocal()
    ca_id = Company.get_ca_id_from_company_id(session, company_id).company_pki_id
    print(ca_id)

    # 1. Générer une clé pour l’agent
    agent_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # 2. Créer une CSR (Certificate Signing Request)
    agent_subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, f"{agent_name}"),
    ])
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(agent_subject)
        .sign(agent_key, hashes.SHA256())
    )


    ca_data = Ca.get_ca_from_id(session, ca_id)

    # 3. Charger la clé + cert CA
    pem_data = ca_data.public_key.replace("\\n", "\n").encode()
    ca_cert = x509.load_pem_x509_certificate(pem_data)
    priv_data = ca_data.private_key.replace("\\n", "\n").encode()
    ca_key = serialization.load_pem_private_key(priv_data, password=None)

    # 4. Signer le certificat de l’agent avec la CA
    agent_cert = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(private_key=ca_key, algorithm=hashes.SHA256())
    )

    key = agent_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())

    with open("agent_cert.pem", "wb") as f:
        f.write(agent_cert.public_bytes(serialization.Encoding.PEM))

#generate_entreprise_pki("Docker-Audit")
generate_agent_pki(1, "Test")