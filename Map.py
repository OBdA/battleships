#! /usr/bin/env python3

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



# This is the Map class. It defines one map with X/Y-Axis and methods for
# accessing and manipulation the status for fields.
#
# The Contructor can be initialized with a dictionary.
class Map(object):
    """
    Create a map object.
    If *initial_map* is defined *x_list* and *y_list* will be dereived from
    this *initial_map*.
    """
    def __init__( self,
                  x_list=tuple('ABCDEFGHIJ'), y_list=tuple(range(1, 11)),
                  initial_map=None):
        assert isinstance(x_list, (str, range, tuple))
        assert isinstance(y_list, (str, range, tuple))

        if not initial_map:
            self.map = {}
            self.x_coor = tuple(x_list)
            self.y_coor = tuple(y_list)
        else:
            self.map = initial_map
            self.x_coor = initial_map.x_coor
            self.y_coor = initial_map.y_coor


    def is_valid_coor(self, coor):
        """
        Returns True if coor is a valid coordinate for this map,
        False otherwise.
        """
        assert isinstance(coor, tuple)

        if len(coor) != 2:
            raise ValueError("coordinates exactly have two elements")

        if coor[0] in self.x_coor and coor[1] in self.y_coor:
            return True
        return False


    # A simple access function for the status of a field.
    def get(self, koor):
        """
        Returns status of a field.
        """
        assert isinstance(koor,tuple),	"request tuple for coordinates"
        assert len(koor) == 2,			"need two coordinates"

        return self.map.get(koor, 'none')


    # This function returns all fields of a map with the given status.
    def get_fields(self, status=None):
        """
        Berechnet alle Felder, die den den Status 'status' haben.
        Ist 'status' nicht gesetzt (default), werden alle Felder zurück
        gegeben, zu denen *kein* Status bekannt ist.

        Returns fields with 'status' (default: unknown status)
        """

        # set 'status' to None if 'none' is given
        if status == 'none': status = None

        # initialize the result fields
        fields = set()

        # I am searching the map (a dictionary) for fields which do not
        # have a status. So I have to loop through all coordinates and see
        # wheter there is some set or not. If nothing is set I add the
        # coordinate to the list.
        if status == None:
            for x in range(len(X_SET)):
                for y in range(len(Y_SET)):
                    if (x,y) not in self.map: fields.add((x,y))
            return fields

        # Here I am searching for fields with a status. Thats easier because
        # I loop through all entries of the dictionary only and look if the
        # fields equals to the status.
        for k,s in self.map.items():
            if status == s: fields.add(k)
        return fields


    # A simple access function for setting the the status of a field.
    def set(self, koor, status):
        """
        Set status of a field.
        """
        assert isinstance(koor,tuple),	"request tuple for coordinates"
        assert len(koor) == 2,			"need two coordinates"
        assert status in STATUS_SET,	"status must be STATUS_SET element"

        self.map[koor] = status
        return


    # This function set the status of all fields to 'status'.
    def set_fields(self, fields, status):
        """
        Setze die Liste der Felder auf iden Feldstatus 'status'.
        Set a list of fields to given status
        """
        assert isinstance(fields, (set,list,tuple)), \
            "'fields' must be a list or tuple of coordinates eg. '[(1,4)]'"

        for (x,y) in fields:
            self.map[(x,y)] = status
        return


    # Here it comes! the terminal output of the map!
    def print(self):
        # I first print all cordinates of the X_SET with enough space for
        # remarks of the Y-Axis
        print( "    ", end="" )
        for x in range(len(X_SET)):
            print( X_SET[x], end=" ")
        print()
        print( "  +", len(X_SET) * '--', sep="")

        # Now print the Y-Axis and for each X-Axis it's element. If it's a
        # integer or float print is as integer. If the element is not a
        # number use the LEGEND to get it's map representation. In both
        # cases print it right assigned with a length of two ({0:2>}).
        for y in range(len(Y_SET)):
            print( "{0:2}|".format(Y_SET[y]), end="")
            for x in range(len(X_SET)):
                val = self.map.get((x,y), 'none')
                if isinstance(val, (int,float)):
                    print("{0:>2}".format(int(val)), end='')
                else:
                    print("{0:>2}".format(LEGENDE[val]), end='')
            print()


    # BE CAREFUL!
    # THIS IS A MYSTIC FUNCTION!
    # It calculates all neighbouring fields. That sounds easy, but with the
    # time I needed some more functionality and this function grows further.
    # IMHO it grows too much and have to bee split up into pieces. If you
    # have a good idea, just fork, hack on it and send me a pull request.
    # Thanks in advance!
    #
    def neighbours(self, fields, status=None, include=False, recursive=False, check=None):
        """
        Returns all neighbour fields of the given field list.
        If 'status' is not None, only fields which status is 'status' will be
        returned.
        If 'include' is True, fields will be included into the result.
        If 'recursive' is True, neighbours() will be called recursivly onto
        the result until all reachable fields are found.
        """
        assert isinstance(fields, set), "'fields' must be set of coordinates"
        assert check == None or check != None and len(fields) == 1,\
            "check only supported for single fields yet"
        assert check == None or check == 'odd' or check == 'even',\
            "check only supports values: None, odd, even"

        # First enhancement: the function should act not only to _one_
        # status, but to a set of status (two and more). To support the old
        # code I change all 'status' into a set (if needed).
        # set 'status' to None if 'none' is given
        if status != None and not isinstance(status, set):
            status = {status}

        # Second enhancement: neighbour() can act recursivly, so I needed
        # the initial 'fields' for the final condition and save them in
        # 'koor_last'.
        koor_last = fields

        # How I do the calculation?
        # I create two list of potential coordinates, one for the X-axis and
        # the other for the Y-axis. I put all the possible coordinates into
        # them (eg. for X-axis that is: x, x-1, x+1).
        result_set = set()
        for koor in fields:
            (x, y) = koor
            pot_x = (x,)
            pot_y = (y,)

            # calculate all possible x and y coordinates
            # left and right
            if x-1 in range(len(X_SET)):
                pot_x = pot_x + (x-1,)
            if x+1 in range(len(X_SET)):
                pot_x = pot_x + (x+1,)

            # up and down
            if y-1 in range(len(Y_SET)):
                pot_y = pot_y + (y-1,)
            if y+1 in range(len(Y_SET)):
                pot_y = pot_y + (y+1,)

            # I loop through all the possible coordinates and add them to
            # the result set if the status of the field is right.
            # add all possible coordinates
            for xi in pot_x:
                for yi in pot_y:
                    stat = self.get((xi,yi))
                    if status == None or stat in status:
                        result_set.add( (xi,yi) )

            # Oh, the recursive thing!
            # First check the 'recursive' flag and the final condition. That
            # is: end recursion if initial field set and calculated field
            # set have equal size. If not: call neighbour function again
            # with the result set as input fields.
            if recursive and len(result_set - koor_last) > 0:
                result_set = self.neighbours(
                    result_set, status, recursive=True, include=True
                )

        # Third enhancement: do remove the initial fields from the result
        # set. This is very practical if you try to mark all fields around
        # of a ship as water...
        if not include:
            #FIXME: if this is recursive, 'fields' do not hold the _inital_
            #       set of fields!
            for koor in fields:
                if koor in result_set: result_set.remove(koor)

        # Fourth enhancement: apply some check ('odd' or 'even') on the
        # result set (eg. get all 'diagonal' fields of a field which was
        # hit)
        if check != None:
            # I use only the first field for the calculation
            field = fields.pop()

            # To do the calculation I define the QSUM of a coordinate as
            # QSUM := (x+y)%2
            # The QSUM can only be '0' or '1', because of the modulo
            # operation. Keep that in mind!
            # A neighbouring field is
            #    'even' when it's QSUM differs from the field's QSUM and
            #    'odd'  when it's equal to the field's QSUM

            # Instead of comparing both of the QSUMs I add one to the
            # field's QSUM if we to check the 'even' fields. So I can
            # easily compare the values directly.
            qsum = (field[0] + field[1]) % 2
            if check == 'even':
                qsum = (field[0] + field[1] + 1) % 2

            # Compute the QSUM of each field and take only the fields which
            # QSUM equals with the computed value above.
            result_set = set([k for k in result_set
                if (k[0] + k[1]) % 2 == qsum
            ])

        return result_set


    def surround_with(self, field, status, what=None):
        """
        Set the surrounding fields of a region. The region is calculated from
        one field and all neighbouring fields with equal status.
        """

        # This is a bit "syntactic sugar" for us. It a wrapper for
        # neighbour() whith a additional set_fields() on the result.
        # But this function looks much prettier than the
        #     set_fields( neighbour( get_region()))
        # thing I have to use otherwise...
        self.set_fields(
            self.neighbours(self.get_region(field), status=what),
            status
        )

        return


    def regions(self, size=1, status=None):
        """
        Returns a list of regions of a minimal size with fields status
        (default :None).
        """
        assert size >  0, "size must be > 0"
        assert size <= max(len(X_SET), len(Y_SET)), \
            "size must not be greater then Y_SET and X_SET"

        # Oh, I am searching for a much shorter variant for this function.
        # Let's bbegin to talk about it.

        # First I initialize the result list.
        positions = []

        # I will searching first for all regions which lying on the X-axis.
        # Afterwards I do the same searching on the Y-axis. So this code has
        # it's code doubled -- just the axis are swapped.

        # Loop through X_SET and Y_SET, in that order.
        for x in range(len(X_SET)):
            # This is the list of the coordinates that may (or may not)
            # build a region of the wanted size.
            pos = []
            for y in range(len(Y_SET)):

                # I add all coodinates of empty fields into the 'pos' list
                # until there is a field which is set.
                if status == None:
                    if (x,y) not in self.map:
                        pos.append((x,y))
                    else:
                        # Have we enough coordinates to build a region with
                        # a minimum of 'size'?
                        # If we have, append the 'pos' list as region to the
                        # result list and pass otherwise. And do not forget
                        # to empty the 'pos' list!
                        if len(pos) >= size:
                            positions.append(pos)
                        else:
                            pass
                        pos = []

                # Here I have to add only fields with a special status. This
                # is quite equal to the code above.
                else:
                    if status == self.get((x,y)):
                        pos.append((x,y))
                    else:
                        if len(pos) >= size:
                            positions.append(pos)
                        pos = []
            if len(pos) >= size:
                positions.append(pos); #print(x,y, 'got region', pos)

        # Now I have done the vertical regions, now we have to do the same,
        # just copy the code above and swap X_SET and Y_SET.
        # It is quite a shame, but I have no idea yet to simplify the
        # code...
        for y in range(len(Y_SET)):
            pos = []
            for x in range(len(X_SET)):
                if status == None:
                    if (x,y) not in self.map:
                        pos.append((x,y))
                    else:
                        if len(pos) >= size:
                            positions.append(pos)
                        else:
                            pass
                        pos = []

                else:
                    if status == self.get((x,y)):
                        pos.append((x,y))
                    else:
                        if len(pos) >= size:
                            positions.append(pos)
                        pos = []
            if len(pos) >= size:
                positions.append(pos)

        return positions


    def get_region(self, field, what=None):
        """
        Returns a region containing 'field' and all fields with equal
        status surrounding it.
        If 'what' is set surrounding fields must have field status 'what'.
        """

        # As default for 'what' use the field status of the given field.
        if what == None:
            what = self.get(field)

        # Now call neighbours() recursivly and get all neighbours of 'field'
        # with the field status 'what'. Return this as region.
        region = self.neighbours(
            {field}, what, include=True, recursive=True
        )

        return region


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


class Test_Map(unittest.TestCase):
    def setUp(self):
        pass
	    #self.map = Map()

    def test_init(self):
        m = Map()
        self.assertIsInstance(m, Map, "simple __init__")

    def test_init_with_coor(self):
        m = Map("ABC", range(1,4))
        self.assertIsInstance(m, Map, "__init__ with coordinate tuples")

    def test_check_coor(self):
        m = Map("ABC", range(1,4))
        self.assertTrue(m.is_valid_coor(('B',1)), "check valid coor")
        self.assertTrue(m.is_valid_coor(('C',3)), "check valid coor")
        self.assertFalse(m.is_valid_coor(('a',1)), "check invalid coor")
        self.assertFalse(m.is_valid_coor(('A',4)), "check invalid coor")



if __name__ == '__main__':
    unittest.main()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#EOF
