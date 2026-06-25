from cacher import Cacher

def loadCache():
    from cacher import Cacher
    return Cacher(cache_file="tests/cache_stub.json")

if __name__ == "__main__":
    cacher = loadCache()
    result = cacher.get("test_key")
    assert result == "test_value", f"Expected 'test_value' but got {result}"
    cacher.add("new_key", "new_value")
    result = cacher.get("new_key")
    assert result == "new_value", f"Expected 'new_value' but got {result}"
    result = cacher.get("nothing")
    assert result is None, f"Expected None but got {result}"
    print("All tests passed!")