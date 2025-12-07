# # 
# # Loading of shard 
# # Routing 
# # eviction

# from dataclasses import dataclass
# import numpy as np
# from typing import List, Tuple
# from enum import Enum, auto

# @dataclass
# class VectorResult:
#     embedding: list[float]
#     distance: float


# class VectorIndex:
#     def __init__(self):
#         self.vectors = []
#         self.keys = []

#     def add(self, key: str, embedding: List[float]):
#         self.keys.append(key)
#         self.vectors.append(np.array(embedding))

#     def deserialize_and_add(self, key: str, raw_stream: bytes):
#         """
#         Deserialize a raw byte stream (e.g., from disk or blob storage) into an embedding
#         and add it to the index.
#         Assumes the stream contains a serialized numpy array (using np.save).
#         """
#         embedding = np.load(raw_stream, allow_pickle=False)
#         self.add(key, embedding.tolist())
    
#     def serialize_to_file(self, key: str, file_path: str):
#         """
#         Serialize the embedding corresponding to the given key and save it to a file.
#         Uses numpy's np.save to write the array to disk.
#         """
#         if key not in self.keys:
#             raise KeyError(f"Key '{key}' not found in index.")
#         idx = self.keys.index(key)
#         np.save(file_path, self.vectors[idx])

#     def get_nearest_neighbours(self, query: List[float], k: int) -> List[VectorResult]:
#         if not self.vectors:
#             return []
#         query_vec = np.array(query)
#         distances = [np.linalg.norm(vec - query_vec) for vec in self.vectors]
#         nearest_indices = np.argsort(distances)[:k]
#         results = []
#         for idx in nearest_indices:
#             results.append(VectorResult(
#                 embedding=self.vectors[idx].tolist(),
#                 distance=distances[idx]
#             ))
#         return results
# # defne a state of loading the shard from either memory, or local storage, or not yet stored


# class ShardState(Enum):
#     NOT_LOADED = auto()
#     IN_MEMORY = auto()
#     ON_DISK = auto()
#     IN_BLOB_STORAGE = auto()

# class Shard:
#     def __init__(self, blob_storage_ref):
#         self.blob_storage_ref = blob_storage_ref
#         self.in_memory_data = None
#         self.disk_data_path = None
#         self.load_state = ShardState.NOT_LOADED

#     def load_data(self, key):
#         if key in self.in_memory_data:
#             return self.in_memory_data[key]
#         elif key in self.disk_data:
#             # Simulate loading from disk to memory
#             self.in_memory_data[key] = self.disk_data.pop(key)
#             return self.in_memory_data[key]
#         else:
#             # Simulate loading from blob storage
#             data = self.blob_storage_ref.get_blob(key)
#             self.in_memory_data[key] = data
#             return data

#     def evict_to_disk(self, key):
#         if key in self.in_memory_data:
#             self.disk_data[key] = self.in_memory_data.pop(key)

   

# class VM_Database_Access:
#   def getNearestNeighbour(embedding: list[float], max_results: int) -> list[VectorResult] :
