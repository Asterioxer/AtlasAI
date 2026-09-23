from app.services.cache import Cache


def test_cache_keys_are_stable_and_namespaced() -> None:
    first = Cache.key("chat", {"workspace": "w1", "question": "hello"})
    second = Cache.key("chat", {"question": "hello", "workspace": "w1"})
    assert first == second
    assert first.startswith("atlasai:chat:")
