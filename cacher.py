import json


class Cacher:
    def __init__(self, cache_file="cache.json"):
        self.cache_file = cache_file
        self.cache = json.load(open(self.cache_file, "r"))

    def get(self, key):
        return self.cache.get(key)

    def add(self, key, value):
        self.cache[key] = value
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)
            f.close()
