# prompt generatio :

# Add an interface and an implementation in python for a 3 layer cache :

# first layer in memory
# second layer on disk
# last layer : back-up on azure blob storage
# The blob storage and file io store need to have an Interface that would allow testing without FILE or blob storage, and add the implementation for the blob and file storege.

# The implementation for loading from file and blob store needs to have async load


from typing import Any, Optional, Protocol
import asyncio

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

# In-memory cache implementation
class MemoryCache:
    def __init__(self):
        self._cache = {}
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value
    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

# File store implementation
class FileStoreImpl:
    def __init__(self, directory: str):
        self.directory = directory
    async def load(self, key: str) -> Optional[Any]:
        path = f"{self.directory}/{key}.cache"
        try:
            async with aiofiles.open(path, "r") as f:
                return await f.read()
        except FileNotFoundError:
            return None
    async def save(self, key: str, value: Any) -> None:
        path = f"{self.directory}/{key}.cache"
        async with aiofiles.open(path, "w") as f:
            await f.write(str(value))
    async def delete(self, key: str) -> None:
        path = f"{self.directory}/{key}.cache"
        try:
            import os
            os.remove(path)
        except FileNotFoundError:
            pass

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
