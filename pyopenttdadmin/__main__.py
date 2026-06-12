import sys

from .auth import randombytes, get_public_key


private_key = randombytes(32)
public_key = get_public_key(private_key)

print("Private key:", private_key.hex().upper())
print("Public key: ", public_key.hex().upper())


