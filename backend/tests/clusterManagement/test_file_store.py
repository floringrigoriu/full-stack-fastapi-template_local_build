import os
import asyncio
import tempfile
import unittest
import aiofiles
import aiofiles.os
from app.coding_problems.ClusterManagement.cache import FileStoreImpl
from app.coding_problems.ClusterManagement.VectorSearch import InMemoryVectorSearch

from .TestUtility import TestUtility

from typing import Any

class TestFileStore(FileStoreImpl):
    async def set(self, key: str, value: Any) -> None:
        await super().set(key, value)
        print(f"persisted key {key}")
        path = self._get_path(key)

        await aiofiles.os.makedirs('~/test_verification', exist_ok = True)
        dest_file_path = f'~/test_verification/{key}'
        async with aiofiles.open(path, "rb") as source_file:
            async with aiofiles.open(dest_file_path, "wb") as destination_file:
                src_fd = source_file.fileno()
                dst_fd = destination_file.fileno()

                # Get the size of the source file to determine the 'count'
                stats = await aiofiles.os.stat(path)
                file_size = stats.st_size

                # Perform the zero-copy file transfer
                bytes_copied = await aiofiles.os.sendfile(dst_fd, src_fd, 0, file_size)
                print(f"Copied {bytes_copied} bytes from {path} to {dest_file_path}, {destination_file.fileno}")


class TestFileStoreImpl(unittest.IsolatedAsyncioTestCase):
    

    async def test_store_and_retrieve_vector_search(self):
        # Setup temp directory for file store
        with tempfile.TemporaryDirectory() as tmpdir:
            store = TestFileStore(directory=tmpdir, max_items=10)
            # Create a VectorSearch instance with 10 vectors
            vs = InMemoryVectorSearch()
            vectors = []
            for i in range(10):
                vec = TestUtility.generate_test_embedding()
                vectors.append((f"id_{i}", vec))
                vs.add_vector(vec, f"id_{i}")
            # Store the instance
            await store.set("vs_key", vs)
            # Retrieve the instance
            loaded_vs = await store.get("vs_key")
            # Check instance is not the same
            assert loaded_vs is not vs
            # Check vectors are the same
            assert hasattr(loaded_vs, "vectors")
            assert len(loaded_vs.vectors) == 10
            for (id1, vec1), (id2, vec2) in zip(vectors, loaded_vs.vectors):
                assert id1 == id2
                assert vec1 == vec2
            # verify retrieval of top 5
            top5 = loaded_vs.top_k(vectors[0][1],5)
            assert len(top5) == 5
            # Clean up
            await store.delete("vs_key")
            assert await store.get("vs_key") is None

