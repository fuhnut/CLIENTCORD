from isal import isal_zlib

ZLIB_SUFFIX = b"\x00\x00\xff\xff"

class GatewayDecompressor:
    def __init__(self) -> None:
        self.inflator = isal_zlib.decompressobj()
        self.buffer = bytearray()

    def decompress(self, data: bytes) -> bytes | None:
        self.buffer.extend(data)
        if len(self.buffer) < 4 or self.buffer[-4:] != ZLIB_SUFFIX:
            return None
        res = self.inflator.decompress(self.buffer)
        self.buffer.clear()
        return res
