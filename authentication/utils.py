from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.backends import default_backend
from django.conf import settings

# Default key locations (relative to project root)
DEFAULT_LOGIN_KEY_DIR = Path(getattr(settings, 'LOGIN_KEY_DIR', settings.BASE_DIR / 'secrets' / 'keys'))
DEFAULT_LOGIN_PRIVATE_KEY = Path(getattr(settings, 'LOGIN_PRIVATE_KEY_PATH', DEFAULT_LOGIN_KEY_DIR / 'login_private.pem'))
DEFAULT_LOGIN_PUBLIC_KEY = Path(getattr(settings, 'LOGIN_PUBLIC_KEY_PATH', DEFAULT_LOGIN_KEY_DIR / 'login_public.pem'))


def _ensure_keys_exist():
    """Generate RSA keypair if missing (no terminal commands needed)."""
    key_dir = Path(DEFAULT_LOGIN_KEY_DIR)
    priv_path = Path(DEFAULT_LOGIN_PRIVATE_KEY)
    pub_path = Path(DEFAULT_LOGIN_PUBLIC_KEY)

    if priv_path.exists() and pub_path.exists():
        return

    key_dir.mkdir(parents=True, exist_ok=True)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()

    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    priv_path.write_bytes(priv_bytes)
    pub_path.write_bytes(pub_bytes)


def _load_private_key(path: Path) -> RSAPrivateKey:
    with path.open('rb') as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())


def get_login_public_key_pem() -> Optional[str]:
    """Return public key PEM as string if available, else None."""
    _ensure_keys_exist()
    path = Path(DEFAULT_LOGIN_PUBLIC_KEY)
    if not path.exists():
        return None
    return path.read_text(encoding='utf-8')


def decrypt_login_password(ciphertext_b64: str) -> str:
    """Decrypt base64 ciphertext with private key using RSA-OAEP SHA-256."""
    _ensure_keys_exist()
    path = Path(DEFAULT_LOGIN_PRIVATE_KEY)
    if not path.exists():
        raise FileNotFoundError(f"Login private key not found at {path}")

    private_key = _load_private_key(path)
    ciphertext = base64.b64decode(ciphertext_b64)
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return plaintext.decode('utf-8')