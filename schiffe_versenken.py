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
	'hit':		'+',
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
	def __init__(self, dict=None):
		if dict == None:
			self.map = {}
		else:
			self.map = dict
		self.rand = random.Random()

	def status(self, koor):
		"""Returns status of one field."""

		assert len(koor) == 2, "request tuple for coordinates"
		return self.map.get(koor, LEGENDE['none'])

	def versenkt(self, koor):
		assert len(koor) == 2, "request tuple for coordinates"

		fields = self.nachbarn([koord], feld=LEGENDE['hit'], recursiv=True)
		self._set_fields(fields, LEGENDE['sunk'])

	def treffer(self, koor):
		assert len(koor) == 2, "request tuple for coordinates"
		self.map[koor] = LEGENDE['hit']

	def wasser(self, koor):
		assert len(koor) == 2, "request tuple for coordinates"
		self.map[koor] = LEGENDE['water']


	# Setze die Liste der Felder auf 'status'
	def _set_fields(self, fields, status):
		"""Set a list of fields to given status"""
		assert isinstance(fields, (set,list,tuple)), \
			"'fields' must be a list or tuple of coordinates eg. '[(1,4)]'"

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
	def nachbarn(self, koor_list, feld=None, include=False, recursive=False):
		"""Returns all neighbour fields of the given field list."""
#		assert isinstance(koor_list, [set,list]), \
#			"'koor_list' must be a list of coordinates"

		# koor_last holds last neighbour set,
		# needed for recursive final condition
		koor_last = set(koor_list)

		result_set = set()
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
						result_set.add( (xi,yi) )

			#FIXME: 'recursiv' not implemented
			# recursive: final condition: neighbour set has not changed
			if recursive and len(result_set - koor_last) > 0:
				#FIXME: make a set
				result_set = set(self.nachbarn(
					result_set, feld, recursive=True, include=True
				))
		# delete original coordinates if 'include' is not set
		if not include:
			for koor in koor_list:
				if koor in result_set: result_set.remove(koor)

		#FIXME: make a set
		return list(result_set)


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


	## Funktion zum Markieren
	def mark_sunken_ship(self, ship):
		self._set_fields(self.nachbarn(ship), LEGENDE['water'])


	## Funktionen zum Auswählen eines Ziels
	def shot_random(self):
		"""Find a random coordinate to bomb onto."""
		return RAND.choice( self._get_fields() )

	def search_ship(self, ship):
		return RAND.choice(self.nachbarn(ship))

	def destroy_ship(self, ship):
		known_ship = self.nachbarn(ship)
		if len(known_ship) == 1: return RAND.choice(self.nachbarn(ship))

		# Lage des Schiffes:
		# eine Achse ist fest, die andere variiert: finde die feste Achse,
		# sortiere die Indizes der variierende Achse um mögliche Koordinaten
		# zu finden.
		x_set = set()
		y_set = set()
		for koord in ship:
			(x,y) = koord
			x_set.add(x)
			y_set.add(y)

		print("x-set:",x_set,"y-set",y_set)
		assert len(x_set)+len(y_set) == len(ship)+1, "ship fields not in a row"
		assert len(y_set) == 1 or len(x_set) == 1, "ship fields not in a row"

		target_list=set()
		if len(x_set) == 1:
			i_var = list(y_set)
			i_var.sort()
			if i_var[0] > 0:
				target_list.add((list(x_set)[0],i_var[0]-1))
			if i_var[-1] < len(Y_SET)-1:
				target_list.add((list(x_set)[0],i_var[-1]+1))
		else:
			i_var = list(x_set)
			i_var.sort()
			if i_var[0] > 0:
				target_list.add((i_var[0]-1,list(y_set)[0]))
			if i_var[-1] < len(X_SET)-1:
				target_list.add((i_var[-1]+1,list(y_set)[0]))
			
		print('target-list:',target_list)
		return target_list



	def find_ship(self, size):
		"""Sucht Schiff auf der Karte, indem das grösste 'Loch' 
		beschossen wird."""

		targets = dict()
		t_map = dict()
		regions = self.regions(size)
		for region in regions:
			val_list = calc_points(region)
			for k,v in val_list:
				t_map[k] += v

		print("T-MAP:", t_map)
		max_val = max(t_map.values())

		targets = {key:val for key,val in t_map.items() if val == max_val}		
		return t_map


## classmethods

def calc_points(region):
	"""Returns dictionary of koordinates with values."""

	values = {}
	n = len(region)
	for i in range(n//2):
		val = 2*(i+1)
		values[region[i]] = val
		values[region[-(i+1)]] = val
	if n%2 != 0:
		i = n//2
		values[region[i]] = 2*(i+1)

	print("VALUES:",values)
	return values


def xy(string):
	if len(string) < 2: return None

	xs = string[0:1].upper()
	ys = int(string[1:])
	try:
		x = X_SET.index(string[0:1].upper())
		y = Y_SET.index(int(string[1:]))
	except:
		return None

	return (x,y)

##
##  MAIN
##

if __name__ == '__main__':

	import re

	ship_count = 0
	sunk_count = 0

	# Set computer ships
	ship_map = Karte()
	for num,ship in SCHIFFE:
		for n in range(num):
			ship_map.place_ship(ship)
			ship_count += 1
	print("\nCaptain!\nEs wurden {0} Schiffe verteilt.".format(ship_count))

	bomb_map = Karte()
	while True:
		line = input( "\nCaptain> " )
		token = line.rstrip("\n").split()
		token.append('')	# empty lines fail to pop()

		cmd = token.pop(0).lower()
		if cmd == 'quit' or cmd == 'ende' or cmd == 'stop':
			break
		elif cmd == '':
			bomb_map.print()
		elif cmd == 'peek':
			ship_map.print()
		elif re.match('[a-z]\d+', cmd):
			koor = xy(cmd)
			if koor == None:
				print( "-- Gib ein Feld bitte mit einem Buchstaben und " \
					"einer Zahl ein.\n-- Zum Beispiel: {0}{1}"\
					.format(RAND.choice(X_SET),RAND.choice(Y_SET)) )
				continue
			elif bomb_map.status(koor) != LEGENDE['none']:
				feld = bomb_map.status(koor)
				print( "-- Oh, Captain!")
				print( "-- Im Feld {0} ist doch schon '{1}'".format(
					X_SET[koor[0]] + str(Y_SET[koor[1]]),
					feld
				))
				continue

			if ship_map.status(koor) == LEGENDE['ship']:
				bomb_map.treffer(koor)

				# check for sunken ship
				ship = set(ship_map.nachbarn( [koor],
					feld=LEGENDE['ship'], include=True, recursive=True
				))
				hits = set(bomb_map.nachbarn( [koor],
					feld=LEGENDE['hit'], include=True, recursive=True
				))
				if len(ship-hits) < 1:
					print( "-- VERSENKT!")
					bomb_map._set_fields(ship, LEGENDE['sunk'])
					bomb_map._set_fields(bomb_map.nachbarn(ship), LEGENDE['water'])
					sunk_count += 1
					bomb_map.mark_sunken_ship(ship)

					# check: all ships sunk?
					if sunk_count >= ship_count:
						ship_map.print()
						bomb_map.print()
						print("\nCaptain!\nHurra, Du hast alle Schiffe gefunden!")
						exit(0)
					if ship_count-sunk_count > 1:
						print("\nCaptain!\nEs fehlen nur noch {0} Schiffe!"\
						.format(ship_count-sunk_count))
					else:
						print("\nCaptain!\nEs fehlt nur noch ein Schiff!")
				else:
					print( "-- TREFFER!" )

			else:
				print( "-- Wasser." )
				bomb_map.wasser(koor)
		else:
			print( "-- Häh? Versuche es mal mit 'hilfe'.")

#EOF
