from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta, UTC
from database.database import dbo
from entity.ca import Ca
from entity.company import Company


def generate_entreprise_pki(name):
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, f"{name}"),
    ])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    company_ca = Ca()
    public_key = ca_cert.public_bytes(serialization.Encoding.PEM)
    private_key = ca_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption())
    expiration_date = ca_cert.not_valid_after_utc
    ca_id = company_ca.add_new_pki(private_key.decode("utf-8"), public_key.decode("utf-8"), expiration_date)
    return ca_id  # <-- AJOUTER CE RETURN


def generate_agent_pki(company_id, agent_name):
    ca_id = Company.get_ca_id_from_company_id(company_id).company_pki_id

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

    ca_data = Ca.get_ca_from_id(ca_id)

    # 3. Charger la clé + cert CA
    pem_data = ca_data.public_key.encode()
    ca_cert = x509.load_pem_x509_certificate(pem_data)
    priv_data = ca_data.private_key.encode()
    ca_key = serialization.load_pem_private_key(priv_data, password=None)

    # 4. Signer le certificat de l’agent avec la CA
    agent_cert = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(private_key=ca_key, algorithm=hashes.SHA256())
    )

    agent_key = agent_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
    agent_cert = agent_cert.public_bytes(encoding=serialization.Encoding.PEM)
    return {"pub": agent_cert.decode("utf-8"), "priv": agent_key.decode("utf-8")}


def verify_certificate(cert_pem_str:bytes , ca_cert_pem_str: bytes):

    try:
        # Charger les certificats depuis des chaînes PEM
        cert = x509.load_pem_x509_certificate(cert_pem_str)
        ca_cert = x509.load_pem_x509_certificate(ca_cert_pem_str)
        ca_public_key = ca_cert.public_key()

        # 1. Vérification de la validité temporelle
        now = datetime.now(UTC)
        if now < cert.not_valid_before_utc or now > cert.not_valid_after_utc:
            return False

        # 2. Vérification de la signature (le cert est signé par la CA)
        ca_public_key.verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),  # ou padding appropriate selon algo
            cert.signature_hash_algorithm,
        )

        # 3. (Optionnel) Vérifier les extensions, ex: basic constraints
        basic_constraints = cert.extensions.get_extension_for_class(x509.BasicConstraints).value
        if basic_constraints.ca:
            return False

        print(">>>>>> Certificat valide et signé par la CA <<<<<<<<")
        return True

    except Exception as e:
        print(f"Échec de la vérification du certificat : {e}")
        return False