import unittest
from .Problem2 import Solution

class TestCountCollisions(unittest.TestCase):
    def setUp(self):
        self.solver = Solution()

    def test_count_collisions(self):
        test_cases = [
            ("RLRSLL", 5),
            ("LLRR", 0),
            ("SSSS", 0),
            ("LSRSRL", 3),
            ("LLL", 0),
            ("RRR", 0),
            ("S", 0),
            ("L", 0),
            ("R", 0),
            ("SRLSR", 2),
        ]
        for directions, expected in test_cases:
            with self.subTest(directions=directions):
                # Arrange
                # Act
                result = self.solver.countCollisions(directions)
                # Assert
                self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
