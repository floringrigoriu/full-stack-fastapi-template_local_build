import random



class TestUtility:
    @staticmethod
    def generate_test_embedding(dim=512, seed=None):
        """
        Generates a random embedding vector for testing purposes.

        Args:
            dim (int): Dimension of the embedding vector.
            seed (int, optional): Random seed for reproducibility.


        """
        if seed is not None:
            random.seed(seed)
        return [random.uniform(-1, 1) for _ in range(dim)]