# prompt generatio :

# Add an interface and an implementation in python for a 3 layer cache :

# first layer in memory
# second layer on disk
# last layer : back-up on azure blob storage
# The blob storage and file io store need to have an Interface that would allow testing without FILE or blob storage, and add the implementation for the blob and file storege.

# The implementation for loading from file and blob store needs to have async load


from typing import Any, Optional, Protocol
import asyncio
from collections import OrderedDict
import os
import aiofiles
import pickle
from .lru import LRUCache

# Interface for file storage
class FileStore(Protocol):
    async def load(self, key: str) -> Optional[Any]:
        ...
    async def save(self, key: str, value: Any) -> None:
        ...
    async def delete(self, key: str) -> None:
        ...

# Interface for blob storage
class BlobStore(Protocol):
    async def load(self, key: str) -> Optional[Any]:
        ...
    async def save(self, key: str, value: Any) -> None:
        ...
    async def delete(self, key: str) -> None:
        ...

class CacheLayer(Protocol):
    async def get(self, key: str) -> Optional[Any]:
        ...
    async def set(self, key: str, value: Any) -> None:
        ...
    async def delete(self, key: str) -> None:
        ...

class MemoryCache(CacheLayer):
    def __init__(self, max_items: int = 100, max_size: int = None):
        def on_evict(key, value):
            pass  # For memory, just remove from cache
        self.lru = LRUCache(max_items=max_items, max_size=max_size, on_evict=on_evict)
        self.lru.set_size_func(lambda v: len(pickle.dumps(v)))

    async def get(self, key: str):
        return self.lru.get(key)

    async def set(self, key: str, value: Any):
        self.lru.set(key, value)

    async def delete(self, key: str):
        self.lru.delete(key)

class FileStoreImpl(CacheLayer):
    def __init__(self, directory: str, max_items: int = 1000, max_size: int = 1024*1024*1024):
        os.makedirs(directory, exist_ok=True)
        def on_evict(key, value):
            path = f"{directory}/{key}.cache"
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
        self.lru = LRUCache(max_items=max_items, max_size=max_size, on_evict=on_evict)
        self.lru.set_size_func(lambda v: len(pickle.dumps(v)))
        self.directory = directory

    def _get_path(self, key: str) -> str:
        return f"{self.directory}/{key}.cache"

    async def get(self, key: str) -> Optional[Any]:
        path = self._get_path(key)
        try:
            async with aiofiles.open(path, "rb") as f:
                data = await f.read()
                value = pickle.loads(data)
            self.lru.set(key, value)
            return value
        except FileNotFoundError:
            return None

    async def set(self, key: str, value: Any) -> None:
        path = self._get_path(key)
        data = pickle.dumps(value)
        async with aiofiles.open(path, "wb") as f:
            await f.write(data)
        self.lru.set(key, value)

    async def delete(self, key: str) -> None:
        path = self._get_path(key)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        self.lru.delete(key)

class AzureBlobStoreImpl(CacheLayer):
    def __init__(self, container_client):
        self.container_client = container_client
    async def get(self, key: str) -> Optional[Any]:
        try:
            blob_client = self.container_client.get_blob_client(key)
            stream = await blob_client.download_blob()
            return await stream.readall()
        except Exception:
            return None
    async def set(self, key: str, value: Any) -> None:
        blob_client = self.container_client.get_blob_client(key)
        await blob_client.upload_blob(str(value), overwrite=True)
    async def delete(self, key: str) -> None:
        blob_client = self.container_client.get_blob_client(key)
        await blob_client.delete_blob()

class NLayerCache:
    def __init__(self, layers: list[CacheLayer]):
        """
        layers: list of cache/storage objects, ordered from fastest (cheapest) to slowest (guaranteed)
        Each layer must implement get(key), set(key, value), delete(key)
        For async layers, use async def for get/set/delete
        """
        self.layers = layers

    async def get(self, key: str) -> Any:
        # Try each layer in order
        for i, layer in enumerate(self.layers):
            value = await layer.get(key)
            if value is not None:
                # Copy to all faster layers above
                for j in range(i):
                    asyncio.create_task(self.layers[j].set(key, value))
                return value
        # Last layer is guaranteed to have the data
        last_layer = self.layers[-1]
        value = await last_layer.get(key)
        # Copy to all faster layers
        for j in range(len(self.layers)-1):
            asyncio.create_task(self.layers[j].set(key, value))
        return value

    async def set(self, key: str, value: Any) -> None:
        # Set in all layers
        for layer in self.layers:
            await layer.set(key, value)

    async def delete(self, key: str) -> None:
        for layer in self.layers:
            await layer.delete(key)

class EfficientVectorStorage(NLayerCache):
    def __init__(self, mem_cache: CacheLayer, file_store: CacheLayer, blob_store: CacheLayer):
        super().__init__([mem_cache, file_store, blob_store])
