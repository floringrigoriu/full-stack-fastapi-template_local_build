import unittest
import random
from app.coding_problems.ClusterManagement.router import Router, ConsistentHashRing
from app.coding_problems.ClusterManagement.VectorSearch import InMemoryVectorSearch

from .TestUtility import TestUtility


class MockCache:
    """Mock cache for testing purposes"""
    def __init__(self, node_id):
        self.node_id = node_id
        self.vector_search = InMemoryVectorSearch()
    
    def top_k(self, query, k):
        return self.vector_search.top_k(query, k)

class TestRouter(unittest.TestCase):
    def setUp(self):
        # Generate 100 random centroids with embedding_length = 512
        self.num_centroids = 100
        self.centroids = [
            TestUtility.generate_test_embedding()
            for _ in range(self.num_centroids)
        ]
        
        # Create a cache factory
        def cache_factory(node_id):
            return MockCache(node_id)
        
        self.cache_factory = cache_factory
        self.initial_real_nodes = 10

    def test_add_node_minimal_disruption(self):
        """Test that adding a node only remaps approximately 1/n of centroids"""
        # Create router with 10 real nodes
        router = Router(
            centroids=self.centroids,
            cache_factory=self.cache_factory,
            virtual_nodes_per_node=1000,
            real_nodes=self.initial_real_nodes
        )
        
        # Record which node serves each centroid before adding
        initial_mapping = {}
        for i, centroid in enumerate(self.centroids):
            centroid_hash = str(centroid)
            node = router.hash_ring.get_node(centroid_hash)
            initial_mapping[i] = node
        
        # Add a new node (10 -> 11)
        router.IncreaseRealNodesCount()
        
        # Record which node serves each centroid after adding
        final_mapping = {}
        new_node_count = 0
        for i, centroid in enumerate(self.centroids):
            centroid_hash = str(centroid)
            node = router.hash_ring.get_node(centroid_hash)
            final_mapping[i] = node
            # print(initial_mapping[i]  != final_mapping[i] ,node, initial_mapping[i] )
            if initial_mapping[i]  != final_mapping[i] :  # The new node
                new_node_count += 1

        # print(zip(final_mapping.items(),initial_mapping.items() ))
        
        # Count how many centroids changed their serving node
        changed_count = sum(1 for i in range(self.num_centroids) 
                          if initial_mapping[i] != final_mapping[i])
        
        # Verify: number of changed centroids < 15
        self.assertLess(changed_count, 15, 
                       f"Too many centroids changed: {changed_count}, expected < 15")
        
        # Verify: new node serves at least num_centroids / (real_nodes * 2)
        min_expected = self.num_centroids // (11 * 2)
        self.assertGreater(new_node_count, min_expected,
                          f"New node serves {new_node_count} centroids, expected > {min_expected}")
        
        # print(f"Add node test: {changed_count} centroids changed, {new_node_count} on new node")

    def test_remove_node_minimal_disruption(self):
        """Test that removing a node only remaps approximately 1/n of centroids"""
        # Create router with 10 real nodes
        router = Router(
            centroids=self.centroids,
            cache_factory=self.cache_factory,
            virtual_nodes_per_node=1000,
            real_nodes=self.initial_real_nodes
        )
        
        # Record which node serves each centroid before removing
        initial_mapping = {}
        for i, centroid in enumerate(self.centroids):
            centroid_hash = str(centroid)
            node = router.hash_ring.get_node(centroid_hash)
            initial_mapping[i] = node
        
        # Remove a node (10 -> 9)
        router.DecreaseRealNodesCount()
        
        # Record which node serves each centroid after removing
        final_mapping = {}
        for i, centroid in enumerate(self.centroids):
            centroid_hash = str(centroid)
            node = router.hash_ring.get_node(centroid_hash)
            final_mapping[i] = node
        
        # Count how many centroids changed their serving node
        changed_count = sum(1 for i in range(self.num_centroids) 
                          if initial_mapping[i] != final_mapping[i])
        
        # Verify: number of changed centroids < 15
        self.assertLess(changed_count, 15,
                       f"Too many centroids changed: {changed_count}, expected < 15")
        
        print(f"Remove node test: {changed_count} centroids changed")

    def test_consistent_hash_ring_properties(self):
        """Test basic properties of the consistent hash ring"""
        ring = ConsistentHashRing(virtual_nodes_per_node=1000, real_nodes=10)
        
        # Verify total virtual nodes
        self.assertEqual(len(ring.ring), 10 * 1000)
        
        # Verify all real nodes are represented
        nodes_in_ring = set(ring.ring.values())
        self.assertEqual(nodes_in_ring, set(range(10)))
        
        # Verify sorted keys are indeed sorted
        self.assertEqual(ring.sorted_keys, sorted(ring.sorted_keys))

if __name__ == "__main__":
    unittest.main()
