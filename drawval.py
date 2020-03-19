from enum import Enum
import math

class Faction(Enum):
	Ally = 0
	Enemy = 1

class DrawOrder(Enum):
	FLOOR = 0
	NPC = 1
	PLAYER = 2

COLOR_BOOST = {
    "warm" : [1.85, 1.35,1.00],		# multipliers for warm colors in r,g,b format
	"cool" : [0.60,0.70,1.8],		# multipliers for cool colors in r,g,b format
	"cool_darken" : 0.3			# multiplier to darken cool colors
	}

"""
	format: [terrain]-[color]: 
	* fg controls the color that the "white" in the PNG files will display
	* bg controls the color that the "black" in the PNG files will display
	* "map" color are more specific.
	* others are mainly reference at this point but shouldn't necessarily be tweaked yet
"""

COLORS = {
	"wall-fg" : (180,140,120),
	"wall-bg" : (55,55,65),
	"floor-trap-fg" : (20,20,25),
	"floor-fg" : (20,20,25),
	"floor-bg" : (55,55,65),
	"pit-fg" : (35,35,35), 
	"pit-bg" : (0,0,0),
	"map-white" : (160,152,142),
	"map-black" : (65,65,65),
	"map-red" : (160,45,45),
	"map-green" : (25,100,25),
	"white" : (255,255,255),
	"black" : (0,0,0),
	"stairs-fg" : (205,110,46),
	"stairs-bg" : (35,35,35),
	"gold-fg" : (245,150,86),
	"boulder-fg" : (185,185,175),
	}

TRAP_CHARS = []

for x in range(0,8):
	TRAP_CHARS.append(274+x)

CHARS  ={
	"person" : 272,
	"remote_trap" : 282,
	"gold" : 283,
	"stairs" : 296,
	"person_fall" : [304,305,306,307,308],
	"floor_give" : [352,353,354,355],
	"boulder" : 337,
	"artifact" : 284
	}