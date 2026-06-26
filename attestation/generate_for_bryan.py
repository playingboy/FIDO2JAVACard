import base64
import datetime
import uuid
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generate_and_format_for_bryan(aaguid_str):
    # 1. Standardize AAGUID formats
    clean_aaguid_hex = aaguid_str.replace("-", "").lower()
    aaguid_bytes = uuid.UUID(clean_aaguid_hex).bytes

    # 2. Generate the Root CA assets (secp256r1)
    root_key = ec.generate_private_key(ec.SECP256R1())
    now = datetime.datetime.utcnow()
    expiry = now + datetime.timedelta(days=3650)

    root_subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "Custom FIDO2 Root CA"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Testing Lab"),
    ])
    
    root_cert = (
        x509.CertificateBuilder()
        .subject_name(root_subject)
        .issuer_name(root_subject)
        .public_key(root_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(expiry)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(root_key, hashes.SHA256())
    )

    # 3. Export to raw binary DER formats
    der_cert = root_cert.public_bytes(serialization.Encoding.DER)
    der_private_key = root_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 4. Encode to Base64 strings (UTF-8 strings for the CLI)
    b64_cert = base64.b64encode(der_cert).decode('utf-8')
    b64_key = base64.b64encode(der_private_key).decode('utf-8')

    # 5. Construct the final terminal command
    command = (
        f"python3 install_attestation_cert.py \\\n"
        f"  --aaguid {clean_aaguid_hex} \\\n"
        f"  --ca-cert-bytes \"{b64_cert}\" \\\n"
        f"  --ca-private-key \"{b64_key}\""
    )
    
    print("\n" + "="*40 + " COPY AND RUN THIS COMMAND " + "="*40)
    print(command)
    print("="*107 + "\n")

# Run using the target YubiKey 5 NFC AAGUID profile string
generate_and_format_for_bryan("2fc0579f-8113-47ea-b116-bb5a8db9202a")
