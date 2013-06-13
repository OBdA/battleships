from builtins import tuple as _tuple
import unittest


class Koor(tuple):
    
    def __new__(_cls,x,y):
        return _tuple.__new__(_cls,[x,y])
    
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Koor" + super().__repr__()
        
    def __str__(self):
        return "X=" + str(self.x) + " Y=" + str(self.y)


if __name__ == '__main__':
    unittest.main()

#EOF
