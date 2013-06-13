from builtins import tuple as _tuple
import unittest


class Coor(tuple):
    """
    Class for arbitrary 2-dimensional coordinates.
    """

    def __new__(_cls,x,y):
        return _tuple.__new__(_cls,[x,y])

    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Coor" + super().__repr__()
        
    def __str__(self):
        return "X=" + str(self.x) + " Y=" + str(self.y)

class Test_Coor(unittest.TestCase):
    def setUp(self):
        self.coor = Coor(13,5)
        
    def test_init_instance(self):
        self.assertIsInstance(self.coor, Coor, msg="Valid instance of Coor")
        self.assertEqual(13, self.coor[0])
        self.assertEqual(5,  self.coor[1])

        self.assertEqual(13, self.coor.x, msg="shorthand for X")
        self.assertEqual(5,  self.coor.y, msg="shorthand for Y")
        
        nx = self.coor.x
        nx += 4
        self.assertEqual(self.coor.x, 13, msg="is immutable")
        
        self.assertEqual("Coor(13, 5)", repr(self.coor),
            msg="check object's repr()"
        )
        self.assertEqual("X=13 Y=5", str(self.coor),
            msg="check object's str()"
        )
        
if __name__ == '__main__':
    unittest.main()

#EOF
