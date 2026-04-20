"""Encryption utilities for secure token storage.

Uses Fernet (symmetric encryption) to protect Strava OAuth tokens.
Encryption key is loaded from the STRAVA_ENCRYPTION_KEY environment variable.
"""

import os

from cryptography.fernet import Fernet, InvalidToken

# Class-level cache for the Fernet instance
_fernet_instance: Fernet | None = None


def _get_fernet() -> Fernet:
    """Get or create a Fernet instance using the configured key."""
    global _fernet_instance
    if _fernet_instance is None:
        key_raw = os.getenv("STRAVA_ENCRYPTION_KEY")
        if not key_raw:
            raise RuntimeError(
                "STRAVA_ENCRYPTION_KEY environment variable is not set. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        # Fernet requires a URL-safe base64-encoded 32-byte key
        _fernet_instance = Fernet(key_raw.encode())
    return _fernet_instance


def encrypt_token(plaintext: str) -> str:
    """Encrypt a plaintext token string.

    Args:
        plaintext: The raw token string to encrypt

    Returns:
        str: URL-safe base64-encoded ciphertext string
    """
    fernet = _get_fernet()
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a Fernet-encrypted token string.

    Args:
        ciphertext: The encrypted token string (URL-safe base64)

    Returns:
        str: Decrypted plaintext token string

    Raises:
        ValueError: If decryption fails (invalid key, corrupted data, or tampered ciphertext)
    """
    fernet = _get_fernet()
    try:
        return fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt token: invalid key or corrupted data") from exc
