#! /usr/bin/python3

#import os

# Feldgrösse
#X_SET = tuple('ABCDEFGHIJ')
X_SET = tuple( range(1, 11))
Y_SET = tuple( range(1, 11))

##
## Definitionen
##

# Mögliche Inhalte eines Kartenfeldes
KARTENFELD = {
	"none": 	".",
	"water":	"o",
	"hit":		"x",
	"sunk":		"*"
}
 
class Karte(object):

	def __init__(self):
		self.map = {}

	def status(self, koor):
		return self.map.get(koor, ' ')
		
	def versenkt(self, koor):
		fields = self._nachbarn(koord, feld='x', recursiv=True)
		self._set_fields(fields, '*')

	def treffer(self, koor):
		self.map[koor] = 'x'

	def wasser(self, koor):
		self.map[koor] = 'o'


	def _set_fields(self, fields, status):
		for (x,y) in fields:
			self.map[(x,y)] = status

	def _get_fields(self, koord, status):
		list = {}
		for k,s in self.map.items():
			if status == s:
				list.update(k)
		return list

	# Returns dictionary of neighbour fields
	#
	#def _nachbarn(self, *koor, feld=None, recursiv=False):
	def _nachbarn(self, koor):
		#FIXME: 'recursiv' not implemented
		list = {}
		(x, y) = koor
		print("X=",x, "Y=",y )
		print("X={0} Y={1}".format(x, y) )
		pot_x = (x,)
		pot_y = (y,)

		# calculate all possible x and y coordinates
		# left side
		if x-1 >= 0:
			pot_x = pot_x + (x-1,)
		# up
		if y-1 >= 0:
			pot_y = pot_y + (y-1,)
		# right side
		if x+1 < len(X_SET):
			pot_x = pot_x + (x+1,)
		# down
		if y+1 < len(Y_SET):
			pot_y = pot_y + (y+1,)

		print( "X=",x, "Y=",y )

		for xi in pot_x:
			for yi in pot_y:
				status = self.status((xi,yi))
				if feld == None or feld == status:
					list[(xi,yi)] = status
		del list[koor]		# itself is not a neighbour
		return list


	def drucke_karte(self):
		# Drucke die Koordinaten A..J
		print( "    ", end="" )
		for x in X_SET:
			print( x, end=" ")
		print()
		print( "  +", len(X_SET) * '--', sep="")

		for y in Y_SET:
			print( "{0:2}| ".format(y), end="")
			for x in X_SET:
				print( self.map.get((x,y), "."), end=" ")
			print()

##
##  Kalkulationsfunktion für den 'besten' Schuss
##
#def berechne_schuss( *, karte=dictionary() )


##
##  MAIN
##

if __name__ == '__main__':
	a = Karte()
	a.wasser(  ('A', 1) )
	a.wasser(  ('J',10) )
	a.treffer( ('E', 5) )

	a.drucke_karte()

#EOF
