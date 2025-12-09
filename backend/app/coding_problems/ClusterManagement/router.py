import hashlib
from typing import List, Protocol, Any
from .VectorSearch import ChunkIndex, InMemoryVectorSearch

class RouterInterface(Protocol):
    def GetSearch(self, targetVector: List[float], topK: int) -> List[Any]:
        ...
    def GetNumberOfRealNodes(self) -> int:
        ...
    def IncreaseRealNodesCount(self) -> None:
        ...
    def DecreaseRealNodesCount(self) -> None:
        ...

class ConsistentHashRing:
    def __init__(self, virtual_nodes: int, real_nodes: int):
        self.virtual_nodes = virtual_nodes
        self.real_nodes = real_nodes
        self.ring = [i % real_nodes for i in range(virtual_nodes)]

    def get_node(self, key: str) -> int:
        h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        v_node = h % self.virtual_nodes
        return self.ring[v_node]

class Router(RouterInterface):
    def __init__(self, centroids: List[List[float]], caches: List[Any], virtual_nodes: int = 10000, real_nodes: int = 10):
        self.chunk_index = ChunkIndex(centroids)
        self.hash_ring = ConsistentHashRing(virtual_nodes, real_nodes)
        self.caches = caches  # List of cache objects for each real node
        self.real_nodes = real_nodes

    def GetSearch(self, targetVector: List[float], topK: int) -> List[Any]:
        # Find closest centroid
        centroid_idx = self.chunk_index.get_closest_centroid(targetVector)
        centroid_vec = self.chunk_index.centroids[centroid_idx]
        # Hash centroid to virtual node, then map to real node
        centroid_hash = str(centroid_vec)
        real_node_idx = self.hash_ring.get_node(centroid_hash)
        cache = self.caches[real_node_idx]
        return cache.top_k(targetVector, topK)

    def GetNumberOfRealNodes(self) -> int:
        return self.real_nodes

    def IncreaseRealNodesCount(self) -> None:
        self.real_nodes += 1
        self.hash_ring = ConsistentHashRing(self.hash_ring.virtual_nodes, self.real_nodes)

    def DecreaseRealNodesCount(self) -> None:
        if self.real_nodes > 1:
            self.real_nodes -= 1
            self.hash_ring = ConsistentHashRing(self.hash_ring.virtual_nodes, self.real_nodes)
