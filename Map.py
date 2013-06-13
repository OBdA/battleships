from builtins import tuple as _tuple
import unittest


class Koor(tuple):
    """
    Class for arbitrary 2-dimensional coordinates.
    """

    def __new__(_cls,x,y):
        return _tuple.__new__(_cls,[x,y])

    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Koor" + super().__repr__()
        
    def __str__(self):
        return "X=" + str(self.x) + " Y=" + str(self.y)

class Test_Koor(unittest.TestCase):
    def setUp(self):
        self.koor = Koor(13,5)
        
    def test_init_instance(self):
        self.assertIsInstance(self.koor, Koor, msg="Valid instance of Koor")
        self.assertEqual(13, self.koor[0])
        self.assertEqual(5,  self.koor[1])

        self.assertEqual(13, self.koor.x, msg="shorthand for X")
        self.assertEqual(5,  self.koor.y, msg="shorthand for Y")
        
        nx = self.koor.x
        nx += 4
        self.assertEqual(self.koor.x, 13, msg="is immutable")
        
        self.assertEqual("Koor(13, 5)", repr(self.koor),
            msg="check object's repr()"
        )
        self.assertEqual("X=13 Y=5", str(self.koor),
            msg="check object's str()"
        )
        
if __name__ == '__main__':
    unittest.main()

#EOF
