import unittest
from .problem1 import Solution

class TestCountTrapezoids(unittest.TestCase):
    def setUp(self):
        self.solver = Solution()

    def test_example1(self):
        points = [[-3,2],[3,0],[2,3],[3,2],[2,-3]]
        # Expected output is 2 (from the problem statement)
        self.assertEqual(self.solver.countTrapezoids(points), 2)

    def test_example2(self):
        points = [[0,0],[1,0],[0,1],[2,1]]
        # Expected output is unknown, set to 0 as placeholder
        self.assertEqual(self.solver.countTrapezoids(points), 1)

    def test_parallepiped(self):
        points = [[-3,2],[-3,0],[2,2],[2,0],[2,-3]]

        self.assertEqual(self.solver.countTrapezoids(points), 3)

if __name__ == "__main__":
    unittest.main()
