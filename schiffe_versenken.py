#! /usr/bin/python3

import random

# Feldgrösse
X_SET = tuple('ABCDEFGHIJ')
Y_SET = tuple( range(1, 11))

# Zufallsgenerator
RAND = random.Random()

##
## Definitionen
##

# Mögliche Inhalte eines Kartenfeldes
LEGENDE = {
	'none': 	'.',
	'water':	'o',
	'hit':		'x',
	'sunk':		'*',
	'ship':		'#'
}

SCHIFFE = [
	# <count>, <ship>
	[1,	{'name': 'Schlachtschiff',	'size': 5}],
	[2,	{'name': 'Kreuzer',			'size': 4}],
	[3,	{'name': 'Zerstörer',		'size': 3}],
	[4,	{'name': 'U-Boot',			'size': 2}]
]
 
class Karte(object):
	def __init__(self):
		self.map = {}
		self.rand = random.Random()

	def status(self, koor):
		"""Returns status of one field."""

		assert len(koor) == 2, "request tuple for coordinates"
		return self.map.get(koor, ' ')
		
	def versenkt(self, koor):
		assert len(koor) == 2, "request tuple for coordinates"

		fields = self.nachbarn([koord], feld='x', recursiv=True)
		self._set_fields(fields, '*')

	def treffer(self, koor):
		assert len(koor) == 2, "request tuple for coordinates"
		self.map[koor] = 'x'

	def wasser(self, koor):
		assert len(koor) == 2, "request tuple for coordinates"
		self.map[koor] = 'o'


	# Setze die Liste der Felder auf 'status'
	def _set_fields(self, fields, status):
		"""Set a list of fields to given status"""
		assert isinstance(fields, (list,tuple)), \
			"'fields' must be a list of coordinates eg. '[(1,4)]'"

		#print("FIELDS:",fields)
		for (x,y) in fields:
			self.map[(x,y)] = status

	# _get_fields
	# Berechnet alle Felder, die den den Status 'status' haben.
	# Ist 'status' nicht gesetzt (default), werden alle Felder zurück
	# gegeben, zu denen *kein* Status bekannt ist.
	def _get_fields(self, status=None):
		"""Returns a list of positions with 'status' (default: unknown status)"""

		list = []
		if status == None:
			for x in range(len(X_SET)):
				for y in range(len(Y_SET)):
					if (x,y) not in self.map: list.append((x,y))
			return list

		for k,s in self.map.items():
			if status == s: list.append(k)
		return list


	# nachbarn
	# Returns list of neighbour fields koordinates
	#
	def nachbarn(self, koor_list, feld=None, recursiv=False):
		"""Returns all neighbour fields of the given field list."""
#		assert isinstance(koor_list, list), "'koor_list' must be a list of coordinates"

		#FIXME: 'recursiv' not implemented
		result_list = {}
		for koor in koor_list:
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

			# add all possible coordinates
			for xi in pot_x:
				for yi in pot_y:
					status = self.status((xi,yi))
					if feld == None or feld == status:
						result_list[(xi,yi)] = status

		# given koordinates are not neighbours
		for koor in koor_list:
			if koor in result_list: del result_list[koor]

		return tuple(result_list.keys())


	def regions(self, size, feld=None):
		"""Returns a list of regions of a minimal size with fields status (default :None)."""
		assert size >  0, "size must be > 0"
		assert size <= max(len(X_SET), len(Y_SET)), \
			"size must not be greater then Y_SET and X_SET"

		positions = []
		# vertical regions
		for x in range(len(X_SET)):
			pos = []
			for y in range(len(Y_SET)):
				if feld == None:
					if (x,y) not in self.map:
						pos.append((x,y))
					else:
						if len(pos) >= size:
							positions.append(pos); #print(x,y, 'got region', pos)
						else:
							pass
						pos = []

				else:
					if feld == self.status(x,y):
						pos.append((x,y))
					else:					   
						if len(pos) >= size:
							positions.append(pos) 
						pos = []
			if len(pos) >= size:
				positions.append(pos); #print(x,y, 'got region', pos)

		# horizontal regions
		for y in range(len(Y_SET)):
			pos = []
			for x in range(len(X_SET)):
				if feld == None:
					if (x,y) not in self.map:
						pos.append((x,y))
					else:
						if len(pos) >= size:
							positions.append(pos); #print(x,y, 'got region', pos)
						else:
							pass
						pos = []

				else:
					if feld == self.status(x,y):
						pos.append((x,y))
					else:					   
						if len(pos) >= size:
							positions.append(pos) 
						pos = []
			if len(pos) >= size:
				positions.append(pos); #print(x,y, 'got region', pos)

		return positions

	def bombard(self):
		"""Find next coordinate to bomb."""

		return RAND.choice( self._get_fields() )
	

	def print(self):
		# Drucke die Koordinaten A..J
		print( "    ", end="" )
		for x in range(len(X_SET)):
			print( X_SET[x], end=" ")
		print()
		print( "  +", len(X_SET) * '--', sep="")

		for y in range(len(Y_SET)):
			print( "{0:2}| ".format(Y_SET[y]), end="")
			for x in range(len(X_SET)):
				print( self.map.get((x,y), "."), end=" ")
			print()


	def place_ship(self, ship):
		"""Returns a random ship position."""
#		assert isinstance(ship, dict), "'ship' must be of type 'dict'"

		(what, size) = ship['name'], ship['size']
		# chose a free region with minimum size of the ship
		region = RAND.choice(self.regions(size))
		if len(region) == 0: return None

		# get a starting point for the ship
		first = RAND.randint(0,len(region)-size)

		# place the ship
		self._set_fields(region[first:first+size], LEGENDE['ship'])

		# place water around all ship fields
		self._set_fields(self.nachbarn(region[first:first+size]), LEGENDE['water'])

		return region[first:first+size]


##
##  MAIN
##

if __name__ == '__main__':

	# Set computer ships
	ship_map = Karte()
	for num,ship in SCHIFFE:
#		print('SHIP:',ship, 'NUM:',num, 'DICT?', isinstance(ship, dict), sep="--")
		for n in range(num):
			print('ship',ship)
			ship_map.place_ship(ship)
	ship_map.print()
		

#EOF
