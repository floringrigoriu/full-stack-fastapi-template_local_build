import hashlib
from typing import List, Protocol, Any, Callable
from .VectorSearch import ChunkIndex, InMemoryVectorSearch, VectorSearchInterface
from .cache import NLayerCache

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
    def __init__(self, virtual_nodes_per_node: int, real_nodes: int):
        self.virtual_nodes_per_node = virtual_nodes_per_node
        self.real_nodes = real_nodes
        self.ring = {}  # Map hash position to real node
        self.sorted_keys = []  # Sorted list of hash positions
        self._initialize_ring()

    def _hash_key(self, key: str) -> int:
        """Generate hash for a key"""
        return int(hashlib.sha256(key.encode()).hexdigest(), 16)

    def _initialize_ring(self):
        """Initialize the ring with virtual nodes for all real nodes"""
        for real_node in range(self.real_nodes):
            self._add_virtual_nodes_for_real_node(real_node)
        self.sorted_keys = sorted(self.ring.keys())

    def _add_virtual_nodes_for_real_node(self, real_node: int):
        """Add virtual nodes for a specific real node"""
        for v_idx in range(self.virtual_nodes_per_node):
            # Create unique key for each virtual node of this real node
            virtual_key = f"node-{real_node}-vnode-{v_idx}"
            hash_pos = self._hash_key(virtual_key)
            self.ring[hash_pos] = real_node

    def _remove_virtual_nodes_for_real_node(self, real_node: int):
        """Remove all virtual nodes for a specific real node"""
        keys_to_remove = []
        for hash_pos, node in self.ring.items():
            if node == real_node:
                keys_to_remove.append(hash_pos)
        for key in keys_to_remove:
            del self.ring[key]

    def get_node(self, key: str) -> int:
        """Get the real node responsible for a given key"""
        if not self.ring:
            return 0
        
        hash_pos = self._hash_key(key)
        
        # Find the first node on the ring >= hash_pos (clockwise)
        for ring_pos in self.sorted_keys:
            if ring_pos >= hash_pos:
                return self.ring[ring_pos]
        
        # Wrap around to the first node
        return self.ring[self.sorted_keys[0]]

    def add_node(self) -> None:
        """Add a new real node - only affects ~1/n of the keys"""
        new_node_id = self.real_nodes
        self.real_nodes += 1
        self._add_virtual_nodes_for_real_node(new_node_id)
        self.sorted_keys = sorted(self.ring.keys())

    def remove_node(self) -> None:
        """Remove a real node - only affects ~1/n of the keys"""
        if self.real_nodes <= 1:
            return
        
        node_to_remove = self.real_nodes - 1
        self._remove_virtual_nodes_for_real_node(node_to_remove)
        self.real_nodes -= 1
        self.sorted_keys = sorted(self.ring.keys())

class Router(RouterInterface):
    def __init__(self, centroids: List[List[float]], cache_factory: Callable[[int],NLayerCache], virtual_nodes_per_node: int = 1000, real_nodes: int = 10):
        self.chunk_index = ChunkIndex(centroids)
        self.hash_ring = ConsistentHashRing(virtual_nodes_per_node, real_nodes)
        self.real_nodes = real_nodes
        self.cache_factory = cache_factory
        self.caches = [cache_factory(node_id) for node_id in range(real_nodes)]

    def GetSearch(self, targetVector: List[float], topK: int) -> VectorSearchInterface:
        # Find closest centroid
        centroid_idx = self.chunk_index.get_closest_centroid(targetVector)
        centroid_vec = self.chunk_index.centroids[centroid_idx]
        # Hash centroid to virtual node, then map to real node
        centroid_hash = str(centroid_vec)
        real_node_idx = self.hash_ring.get_node(centroid_hash)
        cache = self.caches[real_node_idx]
        return cache.get(centroid_vec)

    def GetNumberOfRealNodes(self) -> int:
        return self.real_nodes

    def IncreaseRealNodesCount(self) -> None:
        self.caches.append(self.cache_factory(len(self.caches)))
        self.hash_ring.add_node()

    def DecreaseRealNodesCount(self) -> None:
        self.hash_ring.remove_node()
