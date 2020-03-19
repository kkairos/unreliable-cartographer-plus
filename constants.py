from enum import Enum
from math import radians, cos, sin

class Faction(Enum):
	Ally = 0
	Enemy = 1

class DrawOrder(Enum):
	FLOOR = 0
	NPC = 1
	PLAYER = 2

THETAS = []

for theta in range(1080):
	theta = radians(float(theta/3))
	xd_d = float(cos(theta))
	yd_d = float(sin(theta))
	THETAS.append((xd_d,yd_d))
		
LINES = {
	"top-left" : 201,
	"bottom-right" : 188,
	"top-right" : 187,
	"left-right" : 186,
	"bottom-left" : 200,
	"top-bottom" : 205
	}

SETTINGS = [
	{
		"name" : "Control Scheme",
		"yval" : 3,
		"sel" : 0,
		"desc" : "INPUT_SEL"
	},
	{
		"name" : "Font",
		"yval" : 12,
		"sel" : 0,
		"desc" : "FONT_SEL"
	},
	{
		"name" : "Continue Playing [Esc]",
		"yval" : 15,
		"sel" : 0,
		"desc" : "NO_SEL"
	},
	{
		"name" : "Save and Quit",
		"yval" : 17,
		"sel" : 0,
		"desc" : "NO_SEL"
	}
	]

INPUT_SEL = [
	"789  REST: [5],[.] \n"\
	"4@6  JUMP: [F] \n"\
	"123",
	"QWE  REST: [5],[.] \n"\
	"A@D  JUMP: [F] \n"\
	"ZXC",
	"YKU  REST: [5],[.] \n"\
	"H@L  JUMP: [F] \n"\
	"BJN",
	]
	
INPUT_CON = [
	"Control Scheme:  [C]\n"\
	"Reset Game:      [R]\n"\
	"Quit Game:       [ESC]\n"
]
	
INPUT_SEL_NAME = ["standard numpad", "laptop \"numpad\"", "vi-keys"]

walldraw = []
for x in range(0,16):
	walldraw.append(x+256)
	
pitdraw = []
for x in range(0,8):
	pitdraw.append(x+288)

FONT_FILE = ["uc-tiles-16x16.png"]

TRAPS = {
	0 : {"name" : "Just the Pits"},
	1 : {"name" : "Slip'n'Slide"},
	2 : {"name" : "Fling Back"},
	3 : {"name" : "Oh No!"}
	}

TERRAIN = {
	"wall": {
		"block_m" : True,
		"block_j" : True,
		"block_s" : True,
		"char" : 178,
		"fg" : "wall-fg",
		"bg" : "wall-bg",
		"type" : "wall",
		},
	"solidwall": {
		"block_m" : True,
		"block_j" : True,
		"block_s" : True,
		"char" : 256,
		"fg" : "wall-fg",
		"bg" : "wall-bg",
		"type" : "solidwall",
		},
	"floor" : {
		"block_m" : False,
		"block_j" : False,
		"block_s" : False,
		"char" : 273,
		"fg" : "floor-fg",
		"bg" : "floor-bg",
		"type" : "floor",
		},
	"door" : {
		"block_m" : False,
		"block_j" : False,
		"block_s" : False,
		"char" : 273,
		"fg" : "floor-fg",
		"bg" : "floor-bg",
		"type" : "door",
		},
	"stairs" : {
		"block_m" : False,
		"block_j" : False,
		"block_s" : False,
		"char" : 273,
		"fg" : "stairs-fg",
		"bg" : "stairs-bg",
		"type" : "floor",
		},
	"pit" : {
		"block_m" : True,
		"block_j" : False,
		"block_s" : False,
		"char" : 352,
		"fg" : "pit-fg",
		"bg" : "pit-bg",
		"type" : "pit",
		}

	}