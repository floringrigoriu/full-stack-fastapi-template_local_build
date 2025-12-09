from typing import List, Tuple, Protocol
import heapq
import math

class VectorSearchInterface(Protocol):
    def add_vector(self, vector: List[float], id: str) -> None:
        ...
    def top_k(self, query: List[float], k: int) -> List[Tuple[str, float]]:
        ...

class InMemoryVectorSearch(VectorSearchInterface):
    def __init__(self):
        self.vectors = []  # List of (id, vector)

    def add_vector(self, vector: List[float], id: str) -> None:
        self.vectors.append((id, vector))

    def top_k(self, query: List[float], k: int) -> List[Tuple[str, float]]:
        def euclidean(a: List[float], b: List[float]) -> float:
            return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
        heap = []
        for vid, vec in self.vectors:
            dist = euclidean(query, vec)
            heapq.heappush(heap, (dist, vid))
        return [(vid, dist) for dist, vid in heapq.nsmallest(k, heap)]

class ChunkIndex:
    def __init__(self, centroids: list[list[float]]):
        # Each centroid is a vector, and we use a VectorSearch instance for them
        self.centroids = centroids
        self.vector_search = InMemoryVectorSearch()
        for i, centroid in enumerate(centroids):
            self.vector_search.add_vector(centroid, str(i))

    def get_closest_centroid(self, target: list[float]) -> int:
        # Returns the index of the closest centroid
        top = self.vector_search.top_k(target, 1)
        if top:
            return int(top[0][0])
        return -1