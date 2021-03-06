# Elliptic Curve Implementation

import collections

Coord = collections.namedtuple("Coord", ["x", "y"])


def inv(n, q):
    """
    Find the inverse on n modulus q
    """
    return egcd(n, q)[0] % q


def egcd(a, b):
    """
    This function performs an extended GCD according to euclid's algorithm.
    It finds a pair (s, t) such that a*s + b*t == gcd
    """
    s0, s1, t0, t1 = 1, 0, 0, 1
    while b > 0:
        q, r = divmod(a, b)
        a, b = b, r
        s0, s1, t0, t1 = s1, s0 - q * s1, t1, t0 - q * t1
    return s0, t0, a


class EC(object):
    def __init__(self, a, b, Prime, G, order):
        """
        Initialize an Elliptic Curve, Defined as:
        (y^2 = x^3 + ax + b) modulus Prime
        """
        assert 0 <= a and a < Prime and 0 <= b and b < Prime and Prime > 2
        assert (4 * (a ** 3) + 27 * (b ** 2)) % Prime != 0
        self.a = a                  # Coefficient of x
        self.b = b                  # Constant term
        self.Prime = Prime          # Large prime number - limiting the finite field
        self.G = G                  # Generator point / Base point
        self.zero = Coord(0, 0)     # Zero point

        # Order -
        # An elliptic curve defined over a finite field has a finite number of points.
        # The number of points in a group is called the order of the group.
        self.order = order

    def add(self, p1: Coord, p2: Coord):
        """
        This function returns the addition of two points on the elliptic curve.
        For point addition, we take two points on the elliptic curve and then add them together (R=P+Q).
        """
        # Base Cases
        # Adding a point to (0, 0)
        if p1 == self.zero:
            return p2
        if p2 == self.zero:
            return p1
        # Adding inverse points
        if p1.x == p2.x and (p1.y != p2.y or p1.y == 0):
            return self.zero
        # Calculating the slope (Self-Addition)
        # ((3x^2 + a) / 2y) mod Prime
        if p1.x == p2.x:
            slope = (3 * p1.x * p1.x + self.a) * \
                inv(2 * p1.y, self.Prime) % self.Prime
        # General Case
        # So if we use x^3+ax+b (mod p),
        # and we have two points P (x1,y1) and Q(x2,y2) that we want to add,
        # we calculate the gradient between the points: s=(y1−y2)/(x1−x2)
        # Then to determine the new point R(x3,y3), we use: x=s^2−x1−x2, y=s(x1−x2)−y1
        else:
            temp1 = (p2.y - p1.y)
            temp2 = inv(p2.x - p1.x, self.Prime)
            slope = temp1 * temp2 % self.Prime
        x = (slope * slope - p1.x - p2.x) % self.Prime
        y = (slope * (p1.x - x) - p1.y) % self.Prime
        return Coord(x, y)

    def mul(self, Point, n):
        """
        This function returns the nth multiplication of a point on the elliptic curve.
        The straightforward way of computing a point multiplication is through repeated addition.
        """
        result = self.zero
        addPoint = Point

        # According to Double-and-Add algorithm to Point Multiplication
        # As described in pseudo-code in https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication
        while n > 0:
            if n & 1 == 1:
                result = self.add(result, addPoint)
            addPoint = self.add(addPoint, addPoint)
            n = n >> 1
        return result
