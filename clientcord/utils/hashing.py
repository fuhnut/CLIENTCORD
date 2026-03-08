import xxhash

def hash_key(key: str | bytes) -> bytes:
    if isinstance(key, str):
        key = key.encode("utf-8")
    return xxhash.xxh64(key).digest()
