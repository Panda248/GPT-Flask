import json


class Cacher:
    def __init__(self, cache_file="cache.json"):
        self.cache_file = cache_file
        try:
            with open(self.cache_file, "r") as cache_handle:
                self.cache = json.load(cache_handle)
        except (FileNotFoundError, json.JSONDecodeError):
            self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def add(self, key, value):
        self.cache[key] = value
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)
