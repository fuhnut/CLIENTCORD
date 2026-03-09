import msgspec

class ClientObject(msgspec.Struct, kw_only=True):
    _client = None

    @property
    def client(self):
        return self._client
    
    @property
    def http(self):
        return self._client.http
