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

# In-memory cache implementation with LRU eviction
class MemoryCache:
    def __init__(self, max_items: int = 100, max_size: int = None):
        def on_evict(key, value):
            pass  # For memory, just remove from cache
        self.lru = LRUCache(max_items=max_items, max_size=max_size, on_evict=on_evict)
        self.lru.set_size_func(lambda v: len(pickle.dumps(v)))

    def get(self, key: str):
        return self.lru.get(key)

    def set(self, key: str, value: Any):
        self.lru.set(key, value)

    def delete(self, key: str):
        self.lru.delete(key)

# File store implementation with LRU eviction
class FileStoreImpl:
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

    async def load(self, key: str) -> Optional[Any]:
        path = self._get_path(key)
        try:
            async with aiofiles.open(path, "rb") as f:
                data = await f.read()
                value = pickle.loads(data)
            self.lru.set(key, value)
            return value
        except FileNotFoundError:
            return None

    async def save(self, key: str, value: Any) -> None:
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

# Azure blob store implementation
class AzureBlobStoreImpl:
    def __init__(self, container_client):
        self.container_client = container_client
    async def load(self, key: str) -> Optional[Any]:
        try:
            blob_client = self.container_client.get_blob_client(key)
            stream = await blob_client.download_blob()
            return await stream.readall()
        except Exception:
            return None
    async def save(self, key: str, value: Any) -> None:
        blob_client = self.container_client.get_blob_client(key)
        await blob_client.upload_blob(str(value), overwrite=True)
    async def delete(self, key: str) -> None:
        blob_client = self.container_client.get_blob_client(key)
        await blob_client.delete_blob()

# 3-layer cache implementation
class ThreeLayerCache:
    def __init__(self, mem_cache: MemoryCache, file_store: FileStore, blob_store: BlobStore):
        self.mem_cache = mem_cache
        self.file_store = file_store
        self.blob_store = blob_store

    async def get(self, key: str) -> Any:
        # Try memory cache first
        value = self.mem_cache.get(key)
        if value is not None:
            return value
        
        # Try file storage second
        value = await self.file_store.load(key)
        if value is not None:
            self.mem_cache.set(key, value)
            return value
        
        # Load from blob storage (guaranteed to be present)
        value = await self.blob_store.load(key)
        # Add to memory cache immediately
        self.mem_cache.set(key, value)
        # Asynchronously save to file storage without blocking
        asyncio.create_task(self.file_store.save(key, value))
        return value

    async def set(self, key: str, value: Any) -> None:
        self.mem_cache.set(key, value)
        await self.file_store.save(key, value)
        await self.blob_store.save(key, value)

    async def delete(self, key: str) -> None:
        self.mem_cache.delete(key)
        await self.file_store.delete(key)
        await self.blob_store.delete(key)
