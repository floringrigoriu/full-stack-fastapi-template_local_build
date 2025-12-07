from collections import OrderedDict
from typing import Any, Callable, Optional

class LRUCache:
    def __init__(self, max_items: int = 100, max_size: int = None, on_evict: Optional[Callable[[str, Any], None]] = None):
        self._cache = OrderedDict()
        self.max_items = max_items
        self.max_size = max_size  # in bytes
        self._current_size = 0
        self._get_size = lambda v: len(v) if hasattr(v, '__len__') else 1
        self._on_evict = on_evict

    def set_size_func(self, func: Callable[[Any], int]):
        self._get_size = func

    def get(self, key: str) -> Optional[Any]:
        value = self._cache.get(key)
        if value is not None:
            self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any) -> None:
        size = self._get_size(value)
        if key in self._cache:
            self._current_size -= self._get_size(self._cache[key])
        self._cache[key] = value
        self._cache.move_to_end(key)
        self._current_size += size
        self._evict_if_needed()

    def delete(self, key: str) -> None:
        if key in self._cache:
            self._current_size -= self._get_size(self._cache[key])
            del self._cache[key]

    def _evict_if_needed(self):
        while (self.max_items and len(self._cache) > self.max_items) or \
              (self.max_size and self._current_size > self.max_size):
            old_key, old_value = self._cache.popitem(last=False)
            self._current_size -= self._get_size(old_value)
            if self._on_evict:
                self._on_evict(old_key, old_value)
