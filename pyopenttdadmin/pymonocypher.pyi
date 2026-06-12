from __future__ import annotations
import collections.abc
import typing
__all__: list[str] = ['CryptoAeadCtx', 'blake2b', 'get_public_key', 'shared_keys', 'x25519']
class CryptoAeadCtx:
    """
    Crypto AEAD context, matches the exact crypto OpenTTD uses.
    """
    @staticmethod
    def lock(plaintext: bytes, key: bytes, nonce24: bytes, aad: bytes = b'') -> tuple[bytes, bytes]:
        """
        Stateless encrypt: returns (mac, ciphertext).
        """
    @staticmethod
    def unlock(mac: bytes, ciphertext: bytes, key: bytes, nonce24: bytes, aad: bytes = b'') -> bytes:
        """
        Stateless decrypt: returns plaintext or raises on auth failure.
        """
    def __init__(self, key: bytes, nonce24: bytes) -> None:
        """
        Construct and init from key and nonce.
        """
    def read(self, data: bytes, aad: bytes = b'') -> bytes:
        """
        Verify and decrypt ciphertext with the context. Raises on auth failure; returns plaintext.
        """
    def wipe(self) -> None:
        """
        Securely wipe the context (zeroes key/material).
        """
    def write(self, plaintext: bytes, aad: bytes = b'') -> bytes:
        """
        Encrypt plaintext with the context. Returns (mac, ciphertext).
        """
def blake2b(hash_size: typing.SupportsInt | typing.SupportsIndex, chunks: collections.abc.Iterable) -> bytes:
    """
    Compute BLAKE2b hash of concatenated chunks. 'chunks' is an iterable of bytes-like objects. Returns digest bytes.
    """
def get_public_key(secret_key: bytes) -> bytes:
    """
    Get public key for x25519 from private key.
    """
def shared_keys(our_secret: bytes, their_public: bytes) -> bytes:
    """
    Alias for x25519; returns 32-byte shared secret.
    """
def x25519(our_secret: bytes, their_public: bytes) -> bytes:
    """
    Compute X25519 shared secret from our_secret(32) and their_public(32). Returns 32-byte shared secret.
    """
