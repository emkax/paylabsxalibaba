from imports import *

def generate_signature(private_key_pem, method, endpoint, body, timestamp):
    body_hash = hashlib.sha256(body.encode()).hexdigest()
    string_to_sign = f"{method}:{endpoint}:{body_hash}:{timestamp}"

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
    )

    signature = base64.b64encode(
        private_key.sign(
            string_to_sign.encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    ).decode()

    return signature
