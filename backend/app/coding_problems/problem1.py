# Problem 1 - Coding Problem Example
# leetcode problem : https://leetcode.com/problems/count-number-of-trapezoids-ii/description/?envType=daily-question&envId=2025-12-03
# 3625. Count Number of Trapezoids II
# Hard
# Topics
# premium lock icon
# Companies
# Hint
# You are given a 2D integer array points where points[i] = [xi, yi] represents the coordinates of the ith point on the Cartesian plane.

# Return the number of unique trapezoids that can be formed by choosing any four distinct points from points.

# A trapezoid is a convex quadrilateral with at least one pair of parallel sides. Two lines are parallel if and only if they have the same slope.

 

# Example 1:

# Input: points = [[-3,2],[3,0],[2,3],[3,2],[2,-3]]

# Output: 2

from typing import List

from math import gcd

from collections import defaultdict, Counter

class Solution:
    MODULOER:int = 10**9+7
    def countTrapezoids(self, points: List[List[int]]) -> int:
        # each point has a x,y coordinate    
        # for each pair of points define a normalized gain for the slope of the  line defined by the 2 nodes:
        #  for dx units change in X coordinate this corresponds to dy on the y coordinate
        # the dx,dy are normalizes in sense there are devided by greatest common divisor
        # a special case is for vertical lines, for those the normalization is  dx = 0, dy =1 ( infinite slope)
        
        n = len(points)
        slope_map = set()

        # Compute all slopes between pairs of points and group by slope
        for i in range(n):
            x1, y1 = points[i]
            for j in range(i + 1, n):
                x2, y2 = points[j]
                dx = x2 - x1
                dy = y2 - y1
                if dx == 0:
                    norm_dx, norm_dy = 0, 1  # vertical line
                elif dy == 0:
                    norm_dx, norm_dy = 1, 0  # horizontal line
                else:
                    d = gcd(dx, dy)
                    norm_dx = dx // d
                    norm_dy = dy // d
                    # Ensure consistent direction
                    if norm_dx < 0:
                        norm_dx *= -1
                        norm_dy *= -1   
                slope_map.add((norm_dx, norm_dy))

        # # Now, for each slope, count the number of ways to pick two pairs with parallel sides
        # # Each such combination can form a trapezoid if all four points are distinct
        # trapezoids = set()
        # for pairs in slope_map.values():
        #     m = len(pairs)
        #     for a in range(m):
        #     for b in range(a + 1, m):
        #         i1, j1 = pairs[a]
        #         i2, j2 = pairs[b]
        #         pts = {i1, j1, i2, j2}
        #         if len(pts) == 4:
        #         trapezoids.add(tuple(sorted(pts)))

        result = 0
        for s in slope_map:
            result+=self.countTrapezoidsSlope(points, s)
            result%=self.MODULOER
        
        return result


    def countTrapezoidsSlope(self, points: List[List[int]], slope:[int,int]) -> int:
        moduloer = self.MODULOER
        intercept = defaultdict(set)
        segment_set = defaultdict(Counter)
        for x,y in points:
            sx,sy = slope
            # prompt :add a switch statement for slope to determine the intercept : if sx = 0 ( vertical line), intercept is x and add y.  for horizontal lines sy==0 - intercept is y  and we add x, for the rest of the cases the intercept is the y value for x =0 of a line with slope {sx,sy} passing through point p
            if sx == 0:
                # Vertical line: intercept is x, add y
                intercept[x].add(y)
            elif sy == 0:
                # Horizontal line: intercept is y, add x
                intercept[y].add(x)
            else:
                # General case: intercept is the y-value when x=0 for the line passing through (x, y)
                # y = (sy/sx) * x + b => b = y - (sy/sx) * x
                # To avoid floating point, store as a tuple (numerator, denominator)
                b_num = y * sx - sy * x
                b_den = sx
                d = gcd(b_num, b_den)
                b_num //= d
                b_den //= d
                intercept[(b_num, b_den)].add((x, y))
            
    
        result = 0
        existing_segments =0
        for k,r in intercept.items():
            # for each pair of points p1, p2 in value :
            # compute the square distance between them 
            # increment segment_set[distance][k] by 1
            r_list = list(r)
            for i in range(len(r_list)):
                for j in range(i + 1, len(r_list)):
                    p1 = r_list[i]
                    p2 = r_list[j]
                    if isinstance(p1, tuple) and isinstance(p2, tuple):
                        dx = p1[0] - p2[0]
                        dy = p1[1] - p2[1]
                    else:
                        dx = p1 - p2
                        dy = 0
                    dist_sq = dx * dx + dy * dy
                    segment_set[dist_sq][k] += 1

            r = len(r)
            r = r*(r-1)//2
            result= result + existing_segments*r
            existing_segments+=r
            result%=moduloer
            existing_segments%=moduloer
        
        # the problem needs to take in consideration we dont need to double count for shapes with 2 sets of sides
        # parallet to each other like squares or dimonds shapes
        # for such shape the have equal side sizes
        # for those we need to substract from the results

        # Correction: For slopes with sy > 0, subtract cases where the opposite slope (perpendicular) also exists,
        # which would double-count parallelograms (like squares, rectangles, rhombuses).
        sx, sy = slope
        if sy > 0:
            for segment_size, segment_count in segment_set.items():
                # Only consider segment_count values > 0
                non_zero_counts = [v for v in segment_count.values() if v > 0]
                if non_zero_counts:
                    compesations =0
                    duplicates = 0
                    for v in non_zero_counts:
                        compesations+= duplicates* v
                        duplicates +=v
                    result = (result - compesations) % moduloer
                print (segment_size, non_zero_counts,compesations)
                
        return result