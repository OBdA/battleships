#! /usr/bin/python3
# Terminal based 'battleships' game with a simple KI.
#
# Copyright 2012 by Olaf Ohlenmacher

# Here we are. You may browse through this code and find some helpful
# comments. Helpful in the way to understand the code and to learn
# a little bit about python. So I did ;-)

# The 'import' statement reads python modules.
# For 'battleships' I need some randomness and at one point I need to
# make a "real" copy of a datastructure. So, I import the module 'copy', too.
import random
import copy


## Conventions

# In battleships I need some things like "coordinates", "fields" or the
# result of bombardments. In this section I list them:

# <koor>	is a tuple() containing the coordinates of X- and Y-axis
# <fields>	is a set of coordinates represented by a set of <koor>
# <region>	is a list of connected fields represented by a list of <koor>
# <regions>	is a list of <region>
# <status>	is a status of a field represented by an element of {STATUS_SET}
# <result>	is a result of an bombardment represented by the tuple()
#           (<koor>, <status>)
#
# <shipdef>	is the decription of a ship represented by a dictionary
#           containing the keys 'name' (type of the ship), 'size' (how
#           fields is this ship) and 'num' (how many ships of this type
#           are available
# <ship>	is another name for <region>
# <ships>	is another name for <regions>


##
## Definitions and (hard coded) game configurations
##

# Size of the Maps: possible values for X- and Y-coordinates 
X_SET = tuple('ABCDEFGHIJ')
Y_SET = tuple( range(1, 11))

# Here are all possible status for a field. On the left the identifier,
# the map representation on the right side.
LEGENDE = {
	'none': 	'.',	# no information available
	'water':	'o',	# water field
	'hit':		'+',	# on this field a ship was hit
	'sunk':		'*',	# on this field a ship was sunk
	'ship':		'#'		# 'ship' is for the hidden map only
}

# I need a set of all available status of a field. We take all the
# right sides with keys(), arrange them as a set and put them into
# STATUS_SET.
STATUS_SET = set(LEGENDE.keys())


# Here the set of ships are defined which will be placed by all players.
# It's hard coded -- perhaps some day this will be placed in a config
# file or will be asked interactivly at the beginning of "battleships".
SHIPS = [
	# valid keys: 'num', 'size', 'name'
	{'num': 1, 'size': 5, 'name': 'Schlachtschiff'},
	{'num': 2, 'size': 4, 'name': 'Kreuzer'},
	{'num': 3, 'size': 3, 'name': 'Zerstörer'},
	{'num': 4, 'size': 2, 'name': 'U-Boot'}
]

# Yes, I tried to define some levels of difficulty.
LEVEL = {
	'easy': 80,
	'intermediate': 50,
	'hard': 20
}


# For many thing I need randomness (e.g. the KI) or placing the ships on
# the map. Because all parts of "battleshps" need random numbers we
# define it here with global scope.
#
RAND = random.Random()


# I need some classes for "battleships". I decided for two different
# ones:
# 	Player - an Player object represents all what a player needs: two
# 		maps, a secret map to place his ships and an open map to track his
# 		bombardments and it's results. With these maps Player defines
# 		member functions to interact with these maps and with the player
# 		itself.
#	Map -    an Map object represents the piece of paper for a map and
#		the pencil to write on it. It has member functions to read abd
#		write a field and some esoteric functions to get an idea of
#		what "neighbours" are.
#
# Now let see how I implemented these classes...

# This is the Player class. It defines the type of player, his strenght
# and how to interact with the player.
class Player(object):

	# The init functions set all member of this class. It takes two
	# optional arguments: 'ki' is set to True if this is the computer
	# player, 'level' to define it's strength.
	def __init__(self, ki=False, level=50):

		# Asking for 'human' I prefer before asking for dump, deadly
		# fast calculating machines...so, I called the member 'human'.
		# I called the "level" now 'ki_level' to make clear it is only
		# valid for computer players, not for human ones.
		self.human		= not ki
		self.ki_level	= level

		# The Player needs some counters for counting his ships
		# 'ship_count' which not sunk so far and a list of ships his foe
		# has already. This is 'foeships'.
		self.ship_count	= 0
		self.foeships	= []

		# Now the maps. Because the handling of maps may be difficult,
		# this is encapsulated in another class called 'Map'. I called
		# them 'ships' for the secret map the Player hold his own ships.
		# And 'hits' which is his open map to track the bombardments.
		self.ships	= Map()
		self.hits	= Map()

		# The player (especially the KI) needs to remember the last
		# turn's result. So here we hold space to save is...
		self.last_result = None


		## public methods


	# To play "battleships" you have to set up the game first. Some of
	# this is done automatically while initialize the object (like
	# create space and initializing counters). The placement of the
	# ships should not be done automatically (but it is done yet in
	# __main__).
	# The following function places _one_ ship onto the secret map.
	# Therefor it gets itself (the Player object) and a ship definition,
	# containing the type and size of the ship.
	#
	def place_ship(self, shipdef):
		"""
		Randomly set a ship onto ship map and returns the ship region or
		None if no space is left.
		"""
		assert isinstance(shipdef, dict), "'shipdef' must be of type 'dict'"

		# Get the type and the size of the ship from the ship
		# definition.
		what, size = shipdef['name'], shipdef['size']

		# Just get the map in a shorthand form.
		map = self.ships

		# I calculate a list with all free regions with a minimum size
		# of the ship's size, this is done with 'map.regions(size)'.
		# Then I choose a region randomly from this list an return None
		# to the caller if there is no space left.
		region = RAND.choice(map.regions(size))
		if len(region) == 0: return None

		# The returned region has a _minimum_ size and can be greater
		# then the ship's size. I choose now the part of the region we
		# use for the ship. I get the starting point first.
		# This can be one of 'size - lenght-of-region' fields.
		first = RAND.randint(0,len(region)-size)

		# Now I set 'size' fields (beginning with the first field,
		# choosen above) to the 'ship' status.
		map.set_fields(region[first:first+size], 'ship')

		# Thats important!
		# Because the ships are not allowed to be connected, I set all
		# surrounding fields to 'water'. These fields not empty anymore,
		# so they will not be choosen to place a ship again.
		map.set_fields(
			map.nachbarn(set(region[first:first+size])),
			'water'
		)

		# count this ship and return the region used
		self.ship_count += 1
		return region[first:first+size]


	def cleanup_ships_map(self):
		"""
		Cleanup the ships map of all the helpful water fields.
		"""
		map = self.ships
		map.set_fields(map.get_fields('water'), 'none')


	def save_foes_ships(self, shipdef):
		# I have to copy this dictionary deeply, not copying the
		# reference to it only.
		self.foeships = copy.deepcopy(shipdef)


	def is_all_sunk(self):
		"""
		Returns True when all own ships are sunk.
		"""
		if self.ship_count < 1: return True
		return False


	def turn(self):
		"""
		Play one turn and return a koordninate to bomb the foe's ships.
		Returns None when when player resigns or has no possible turn left.
		"""
		if self.human:
			# This is the human part of turn() -- I do not comment it
			# and left it to the reader...
			if self.last_result:
				lkoor,lstat = self.last_result
				if lstat == 'sunk':
					self.hits.surround_with(lkoor, 'water')

				elif lstat == 'hit':
					self._mark_hit_ship(lkoor)

			bomb_map = self.hits
			ship_map = self.ships

			koor = None		# is a tuple()
			while True:
				line = input( "\nCaptain> " )
				token = line.rstrip("\n").split()
				token.append('')	# empty lines fail to pop()
				cmd = token.pop(0).lower()
				if re.match('^(resign|aufgeben|quit|exit|ende|stop)', cmd):
					exit(0)
				elif re.match('^(hilfe|help)', cmd):
					_hilfe()
				elif re.match('^(skip)', cmd):
					break
				elif cmd == '':
					bomb_map.print()
				elif cmd == 'ships':
					ship_map.print()
				elif cmd == 'strategie':
					t_map = self._best_moves()
					Map(t_map).print()
				elif cmd == 'tmap':
					t_map = self._rate_unknown_fields(int(token[0]))
					Map(t_map).print()
				elif cmd == 'tipp':
					t_map = self._best_moves()
#					Map(t_map).print()
					best_rate = max(t_map.values())
					best_moves= [k for k,v in t_map.items() if v == best_rate]
					print('Mmmm..vieleicht auf {}'.format(as_xy(RAND.choice(best_moves))))
				elif re.match('[a-z]\d+', cmd):
					koor = as_koor(cmd)
					if koor == None:
						print( "-- Gib ein Feld bitte mit einem Buchstaben und " \
							"einer Zahl ein.\n-- Zum Beispiel: {0}{1}"\
							.format(RAND.choice(X_SET),RAND.choice(Y_SET)) )
						continue
					elif bomb_map.get(koor) != 'none':
						feld = bomb_map.get(koor)
						print( "-- Oh, Captain!")
						print( "-- Im Feld {0} ist doch schon '{1}'".format(
							X_SET[koor[0]] + str(Y_SET[koor[1]]),
							feld
						))
						continue
					break
				else:
					print( "-- Häh? Versuche es mal mit 'hilfe'.")
			return koor

		# This is the KI part.
		# I create the 'target_map' with a set of the best moves. On the
		# following lines I will add some more fields with calculated
		# 'move rates' which helps to find the best move.
		#
		# _best_moves() tries to find the field with the highest
		# possibility to find a foe's ship.
		target_map = self._best_moves()

		# get the highest rate from the target map
		best_rate  = max(target_map.values())

		# ...and get the best moves out of the target map
		best_moves = [xy for xy,val in target_map.items() if val == best_rate]

		# Now, get one of the best moves and return it!
		f =  RAND.choice(best_moves)
		print('foes turn: {} with {} points'.format(f, target_map[f]))
		return f


	def bomb(self, koor):
		"""
		Bomb a field on the ship map and return the result.
		"""
		assert isinstance(koor, tuple), "Need a tuple as field coordinate."

		result = None
		map = self.ships

		# get the status of the bombed field
		status = map.get(koor)
		if status == 'ship' or status == 'hit':
			# We are hit!
			map.set(koor, 'hit')

			# check wheter our ship was completly sunk
			# get all neighbouring 'ship' or 'hit' fields
			ship = map.nachbarn(
				{koor}, status={'ship', 'hit'}, include=True, recursive=True
			)
			# get all 'hit' fields only
			hits = map.nachbarn(
				{koor}, status='hit', include=True, recursive=True
			)
#			print('SHIP:',ship,'HITS:',hits)

			# compare the number of fields in the sets, if there more
			# hits than ship fields this ship must be sunk
			if len(ship-hits) < 1:
				map.set_fields(ship, 'sunk')
				self.ship_count -= 1
				result =  (koor, 'sunk')
			else:
				result =  (koor, 'hit')

		# Oh yeah, only water was hit
		elif status == 'none' or status == 'water':
			map.set(koor, 'water')
			result =  (koor, 'water')

		# If something gets wrong we raise an exception
		if result == None:
			raise Exception("sync error in protocol", (koor, status))

		# send a message and return
		self.send_message('foe_has_' + result[1], result)
		return result


	def handle_result(self, result):
		"""
		Handle all the possible results of a bombardment
		"""
		assert isinstance(result, tuple), "<result> must be an tuple (koor,status)"

		# we got the result, consisting of a coordinate and a result
		koor,status = result
		assert status in STATUS_SET, "no valid <status> in <result>"
		map = self.hits

		# Great! We sunk a ship!
		if status == 'sunk':
			map.set(koor, status)
			ship = map.nachbarn( {koor}, {'hit','sunk'}, True, True)

			# mark sunken ship in my map
			map.set_fields(ship, 'sunk')

			# find the sunken ship in the list of foe's ships and count
			# it down -- save the name for the following message
			name = None
			for s in self.foeships:
				if s['size'] == len(ship):
					s['num'] -= 1
					name = s['name']
					break
			if name == None:
				raise Exception("Not existing ship sunk", [result,ship,len(ship)])

			# send the message which ship was sunk
			self.send_message('result_sunk', name, ship)

		# Good, we hit a ship.
		elif status == 'hit':
			map.set(koor, status)
			self.send_message( 'result_' + status, result )

		# Oh, nothing noticeable hit.
		elif status == 'water':
			map.set(koor, status)
			self.send_message( 'result_' + status, result )

		# Damn! There must be something wrong...
		else:
			raise Exception("unable to handle result", result)

		# Save the last result for later use and return
		self.last_result = result
		return


	# This function does the communication part with the players. All
	# possible messages are listed here. If you want to localize you
	# only have to do this in this function.
	# FIXME: do localize all messages
	def send_message(self, msgid, *args):
		"""
		Send message to the player (only for interactive mode).
		"""
		if not self.human: return

		# Perhaps, we should ask the player for his name and get it from
		# the object here.
		#FIXME: ask the player for his name in init code and use it here
		name = 'Kapitän'
		if msgid == 'ships_distributed':
			print("{}! Es wurden {} Schiffe verteilt.".format(
				name, args[0]
			))

		elif msgid == 'result_sunk':
			print("{}! Wir haben ein {} versenkt!".format(
				name, args[0]
			))

		elif msgid == 'result_hit':
			print("{}! Wir haben auf Feld {} ein Schiff getroffen!".format(
				name, as_xy(args[0][0])
			))

		elif msgid == 'result_water':
			print("{}! Wasser.".format(
				name, args[0]
			))

		elif msgid == 'foe_has_sunk':
			print("{}! Unser Gegner hat unser Schiff bei {} versenkt!".format(
				name, as_xy(args[0][0])
			))

		elif msgid == 'foe_has_hit':
			print("{}! Unser Gegner hat unser Schiff bei {} getroffen!".format(
				name, as_xy(args[0][0])
			))

		elif msgid == 'foe_has_water':
			print("{}! Unser Gegner macht Wellen bei {}.".format(
				name, as_xy(args[0][0])
			))

		elif msgid == 'you_win':
			print("{}! DU HAST GEWONNEN!".format(name))

		elif msgid == 'you_lost':
			print("{}! DU HAST LEIDER VERLOREN!".format(name))

		else:
			print("UNKNOWN MESSAGE:", msgid, '>>', args)

		return


	def _mark_hit_ship(self, field):
		"""
		Mark the fields around a hit field which are 'diagonal', because
		there can not be another ship.
		"""
		assert isinstance(field, tuple), "field must be a tuple"
		assert field[0] in range(len(X_SET)) and field[1] in range(len(Y_SET)),\
			"field must be element of (X_SET, Y_SET)"

		# find all 'diagonal' fields and mark them as water
		self.hits.set_fields(
			self.hits.nachbarn({field}, filter='odd'),
			'water'
		)

		return


	# Oh yeah -- the magical function which calculates the best moves.
	# This is the one which give you a hint or let the computer move.
	def _best_moves(self):
		"""
		Calculate the best move and return the coordinates.
		"""

		# I use a level for this KI, ranging from 0 to 100. If a human
		# player ask fo a hint use the maximum value to get the best
		# result.
		level = self.ki_level
		if self.human: level = 100

		# I create a map with a rate for each field. The field with the
		# highest rate will be bombed...
		rate_map = dict()

		# I use the result from the last turn to calculate some
		# additional information, eg. to mark a hit field or a sunken
		# ship. All thios is done with a certain possibility only.
		if self.last_result != None:
			field, status = self.last_result

			# to mark the 'diagonal' fields of a hit field is hard. (I
			# got it after thinking a lot myself.)
			if status == 'hit' and RAND.randint(0,100) <= level + LEVEL['hard']:
				self._mark_hit_ship(field)
				#print('level:',level,'mark_hit_ship_at:',field)

			# mark a sunken ship my son got easily -- so it should easy
			# too.
			if status == 'sunk' and RAND.randint(0,100) <= level + LEVEL['easy']:
				self.hits.surround_with(field, 'water')
				#print('level:',level,'ship_is_sunk')

			# got a rate for unknown fields i give the 'intermediate'
			# level. My son got the idea fast (to bomb the big hole at
			# the map), but to find the right field on the big holes are
			# quite difficulty. 
			if RAND.randint(0,100) <= level + LEVEL['intermediate']:
				# what is the maximum ship size we are searching for?
				maximum = max(
					[shipdef['size'] for shipdef in self.foeships \
					if shipdef['num'] > 0]
				)
				# get the rate map for the unknown fields and add them
				# to our target map (rate_map)
				rmap = self._rate_unknown_fields(size=maximum)
				for f in rmap.keys():
					rate_map[f] = rate_map.get(f,0) + rmap[f]
				#print('level:',level,'rate_fields_size:',maximum)

			# suppose we hit a ship on a turn formerly. This code trys
			# to sunk all this ships we find.
			hits = self.hits.get_fields('hit')
			if len(hits) > 0 and RAND.randint(0,100) <= level + LEVEL['easy']:
				#print('level:', level, 'destroy_ship:',hits, end=' ')

				# get one field, get the ship and find all empty neighbours
				field = hits.pop()
				fields = self.hits.nachbarn(
					self.hits.get_region(field),
					status='none'
				)

				# add rate to all this empty fields possibly containing
				# the remaining ship -- use a static value of 20.
				for f in fields:
					rate_map[f] = rate_map.get(f,0) + 20

		# This is a fall-back.
		# If we are unlucky and get no target map this will rate all
		# empty field with 1. At a result an empty field will be bombed
		# randomly.
		if self.last_result == None or len(rate_map) < 1:
			rate_map = {koor:1 for koor in self.hits.get_fields('none')}
			#print('LEVEL', level, 'random_field')
		#print('LEVEL', level, 'RATED MAP IS:')
		#Map(rate_map).print()

		return rate_map


	def _rate_unknown_fields(self, size=1, rate=1):
		"""
		Rate unknown fields of the open map and return a <target map>.
		The Parameter 'size' is the minimal size of a region (default: 1). 
		Bewertet unbekannte Felder der Map und gibt eine <target map>
		zurück. The parameter 'rate' is the basis to calculate the 
		<target map> (default: 1).
		"""

		# initialize the <target map> as an dictionary
		t_map = dict()

		# get all regions with the minimum of 'size'
		regions = self.hits.regions(size)

		# now get all regions found and calculate a value list for each
		# region. the calculated values are merged with the <target map>.
		# The function calc_points() calculates for each field of a region a
		# value, depending on the distance from the center of the region.
		# fields in the center have the highest value, fields at the edge
		# the lowest.
		for region in regions:
			val_list = calc_points(region, rate)
			for k,v in val_list.items():
				t_map[k] = t_map.get(k, 0) + v

		return t_map



# This is the Map class. It defines one map with X/Y-Axis and methods for
# accessing and manipulation the status for fields.
#
# The Contructor can be initialized with a dictionary.
class Map(object):
	def __init__(self, dict=None):
		if dict == None:
			self.map = {}
		else:
			self.map = dict


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

		# initialize the result list
		list = set()

		# I am searching the map (a dictionary) for fields which do not
		# have a status. So I have to loop through all coordinates and see
		# wheter there is some set or not. If nothing is set I add the
		# coordinate to the list.
		if status == None:
			for x in range(len(X_SET)):
				for y in range(len(Y_SET)):
					if (x,y) not in self.map: list.add((x,y))
			return list

		# Here I am searching for fields with a status. Thats easier because
		# I loop through all entries of the dictionary only and look if the
		# fields equals to the status.
		for k,s in self.map.items():
			if status == s: list.add(k)
		return list


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
	def nachbarn(self, fields, status=None, include=False, recursive=False, filter=None):
		"""
		Returns all neighbour fields of the given field list.
		If 'status' is not None, only fields which status is 'status' will be
		returned.
		If 'include' is True, fields will be included into the result.
		If 'recursive' is True, nachbarn() will be called recursivly onto
		the result until all reachable fields are found.
		"""
		assert isinstance(fields, set), "'fields' must be set of coordinates"
		assert filter == None or filter != None and len(fields) == 1,\
			"filter only supported for single fields yet"
		assert filter == None or filter == 'odd' or filter == 'even',\
			"filter only supports values: None, odd, even"

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
				result_set = self.nachbarn(
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

		# Fourth enhancement: apply some filter ('odd' or 'even') on the
		# result set (eg. get all 'diagonal' fields of a field which was
		# hit)
		if filter != None:
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
			# field's QSUM if we to filter the 'even' fields. So I can
			# easily compare the values directly.
			qsum = (field[0] + field[1]) % 2
			if filter == 'even':
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
			self.nachbarn(self.get_region(field), status=what),
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


#WORKING
	def get_region(self, field, what=None):
		"""
		Returns a region containing 'field' and all fields with equal
		status surrounding it.
		If 'what' is set surrounding fields must have field status 'what'.
		"""

		# set default field status to search for
		if what == None:
			what = self.get(field)

		# get all neighbours of 'field' with equal field status
		region = self.nachbarn(
			{field}, what, include=True, recursive=True
		)

		return region


## classmethods

def _hilfe():
	print( """
ende  - Du gibst auf und beendest das Spiel.
skip  - Du verzichtest auf Deinen Zug.
ships - Schau auf Deine geheime Karte.
tipp  - Ich gebe Dir einen Tipp.
hilfe - Ich zeige Dir die Befehle, die ich verstehe.

Gibst Du mir keine Eingabe, zeige ich Dir Deine Karte.
Gibst Du mir einen Buchstaben und eine Zahl, wie A4, oder D10
schießt Du auf dieses Feld.

Was soll ich tun?
""")
	return


def calc_points(region, rate=1):
	"""
	Returns <target map> of the given region.
	Parameter 'rate' gives the base rate (default: 1).
	"""

	values = {}
	n = len(region)
	for i in range(n//2):
		val = rate*(i+1) + n
		values[region[i]] = val
		values[region[-(i+1)]] = val
	if n%2 != 0:
		i = n//2
		values[region[i]] = rate*(i+1) + n

	return values


def as_xy(koor):
	return X_SET[koor[0]] + str(Y_SET[koor[1]])


def as_koor(string):
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

	# Set computer ships
	p1 = Player()
	p2 = Player(ki=True, level=00)
	for ship in SHIPS:
		num = ship['num']
		for n in range(num):
			p1.place_ship(ship)
			p2.place_ship(ship)

	p1.cleanup_ships_map()
	p1.send_message('ships_distributed', p1.ship_count)
	p2.save_foes_ships(SHIPS)

	p2.cleanup_ships_map()
	p2.send_message('ships_distributed', p2.ship_count)
	p1.save_foes_ships(SHIPS)

	# initialze turn counter
	turn = 0

	# create a player's list
	player = list()
	player.append(p1)
	player.append(p2)

	# save number of players
	num_player = len(player)

	# Nobody has won or loose, yet
	winner	= None
	loser	= None
	while True:
		print('turn',turn,'num_player',num_player)

		# calculate which player is active or passive
		active  = player[turn   % num_player]
		passive = player[(turn+1) % num_player]

		if active.is_all_sunk():
			loser	= active
			winner	= passive
			break
		koor = active.turn()
		if koor == None:
			# skip this turn
			pass
		else:
			# take turn and handle result
			active.handle_result(passive.bomb(koor))

		turn += 1

	# END OF GAME
	winner.send_message('you_win')
	loser.send_message('you_lost')
	exit(0)

#EOF
