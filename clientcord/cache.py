import lmdb
import msgspec
import os
from typing import Any
from .utils.hashing import hash_key

class LMDBCache:
    def __init__(self, path: str = ".clientcord_cache", map_size: int = 104857600) -> None:
        os.makedirs(path, exist_ok=True)
        self.env = lmdb.open(path, map_size=map_size, writemap=True, readahead=True)

    def set(self, key: str | bytes, value: Any) -> None:
        h_key = hash_key(key)
        data = msgspec.json.encode(value)
        with self.env.begin(write=True) as txn:
            txn.put(h_key, data)

    def get(self, key: str | bytes, typ: type[msgspec.Struct]) -> msgspec.Struct | None:
        h_key = hash_key(key)
        with self.env.begin() as txn:
            data = txn.get(h_key)
            if data is not None:
                return msgspec.json.decode(data, type=typ)
        return None

    def delete(self, key: str | bytes) -> None:
        h_key = hash_key(key)
        with self.env.begin(write=True) as txn:
            txn.delete(h_key)
