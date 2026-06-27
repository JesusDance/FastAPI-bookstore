class FakeRedis:
    def __init__(self):
        self.storage = {}

    async def set(self, name: str, value: dict, ex=None):
        self.storage[name] = value

    async def get(self, key: str) -> dict:
        return self.storage.get(key)

    async def delete(self, key: str) -> None:
        self.storage.pop(key, None)

    async def scan_iter(self, match=None):
        for key in list(self.storage):
            yield key


fake_redis = FakeRedis()


def override_get_redis_client():
    return fake_redis
