import tcod
import constants as cx
import drawval
from random import randint

# Movement
def draw_all(map,map_console,entities,fov):
	for y in cx.DrawOrder:
		for x in entities:
			if fov[x.x][x.y] >0:
				if x.draw_order == y:
					draw_e(map_console,fov,x,True)
			elif (map.t_[x.x][x.y].explored and (x.draw_order == cx.DrawOrder.FLOOR)):
				draw_e(map_console,fov,x,True)
	
def clear_all(map,map_console,entities):
	for x in entities:
		if map.t_[x.x][x.y].explored:
			clear_e(map_console,x)

def draw_e(map_console,fov,x,out_of_sight=False):
	warm_fg, cool_fg = color_mods(drawval.COLORS[x.fg])
	map_console.put_char(x.x, x.y, x.char, tcod.BKGND_DEFAULT)
	map_console.fg[x.x,x.y] = color_diff(warm_fg,cool_fg,fov[x.x][x.y])
	
def clear_e(map_console,x):
	map_console.put_char(x.x, x.y, ord(" "), tcod.BKGND_DEFAULT)

def draw_paper_map(paper_map,map_console):
	
	for y in range(map_console.height):
		for x in range(map_console.width):

			map_console.put_char(x, y, paper_map.t_[x][y].char, tcod.BKGND_DEFAULT)
			map_console.fg[x,y] = paper_map.t_[x][y].fg
			map_console.bg[x,y] = paper_map.t_[x][y].bg

def draw_map(map,paper_map,map_console,fov):
	
	for y in range(map_console.height):
		for x in range(map_console.width):
			#get warm and cool versions of colors
			
			warm_fg, cool_fg = color_mods(map.t_[x][y].fg)
			warm_bg, cool_bg = color_mods(map.t_[x][y].bg)
			
			if fov[x][y] > 0:
				map_console.put_char(x, y, map.t_[x][y].char, tcod.BKGND_DEFAULT)
				map_console.fg[x,y] = color_diff(warm_fg,cool_fg,fov[x][y])
				map_console.bg[x,y] = color_diff(warm_bg,cool_bg,fov[x][y])	
			elif fov[x][y] == 0 and map.t_[x][y].explored == True:
				warm_fg, cool_fg = color_mods(map.t_[x][y].fg)
				warm_bg, cool_bg = color_mods(map.t_[x][y].bg)
				map_console.fg[x,y] = cool_fg
				map_console.bg[x,y] = cool_bg
			elif paper_map.t_[x][y].explored == False:
				if explored_around(map,x,y):
					map_console.fg[x,y] = paper_map.t_[x][y].fg
					map_console.bg[x,y] = color_darken(paper_map.t_[x][y].bg)
					paper_map.t_[x][y].explored = True

#	this may need to be cleaned up later

#	r = colortriplet[0], g = colortriplet[1], b = colortriplet[2]

def color_darken(colortriplet):
	return (int(colortriplet[0]*.85),int(colortriplet[1]*.85),int(colortriplet[2]*.85))

def explored_around(map,x,y):
		for z in range(0,9):
			x2 = (x-1)+(z%3)
			y2 = (y-1)+(z//3)
			if x2 > -1 and x2 < map.width and y2 > -1 and y2 < map.height:
				if map.t_[x2][y2].explored == True:
					return True
		return False

def color_diff(warmtriplet, cooltriplet, warm_mod):
	wr,wg,wb = warmtriplet
	cr,cg,cb = cooltriplet
	
	dr,dg,db = int((cr-wr)*(1-warm_mod)), int((cg-wg)*(1-warm_mod)), int((cb-wb)*(1-warm_mod))
	
	return wr+dr,wg+dg,wb+db

def color_mods(colortriplet):
	r,g,b = colortriplet
	r2,g2,b2 = colortriplet
	
	warm = []
	cool = []
	
	for x in range(0,3):
		warm.append(drawval.COLOR_BOOST["warm"][x])
		cool.append(drawval.COLOR_BOOST["cool"][x])
	
	cool_darken = drawval.COLOR_BOOST["cool_darken"]
	
	#warm
	r = min(255,int(r*warm[0]))
	g = min(255,int(g*warm[1]))
	b = min(255,int(b*warm[2]))
	
	#cool
	r2 = min(255,int(r*cool[0]))
	g2 = min(255,int(g*cool[1]))
	b2 = min(255,int(b*cool[2]))
	r2 = int(r2*cool_darken)
	g2 = int(g2*cool_darken)
	b2 = int(b2*cool_darken)
	
	return (r,g,b),(r2,g2,b2)
	
def draw_con(main_console,map_console,xpos,ypos):
	map_console.blit(
		main_console,
		xpos,ypos, #dest
		0,0, #src
		map_console.width,map_console.height, #w&h
		1.0,1.0, #fg,bg alpha
		None
		)

def legend_print(console,chars,x,y):
	
	console.print(x,y,"MAP LEGEND",drawval.COLORS["white"],drawval.COLORS["black"],tcod.BKGND_DEFAULT,tcod.LEFT)
	
	y+=2
	
	for z in range(0,4):

		z2 = z*2
		console.put_char(x+0,y+z, ord("*"),tcod.BKGND_DEFAULT)
		console.put_char(x+1,y+z, chars[z],tcod.BKGND_DEFAULT)
		console.put_char(x+2,y+z, ord("*"),tcod.BKGND_DEFAULT)
		console.fg[x][y+z] = drawval.COLORS["map-red"]
		console.fg[x+1][y+z] = drawval.COLORS["map-red"]
		console.fg[x+2][y+z] = drawval.COLORS["map-red"]
		console.print(x+3,y+z,cx.TRAPS[z]["name"],drawval.COLORS["white"],drawval.COLORS["black"],tcod.BKGND_DEFAULT,tcod.LEFT)
	
	console.print(x,y+5,"Other",drawval.COLORS["white"],drawval.COLORS["black"],tcod.BKGND_DEFAULT,tcod.LEFT)
	
	console.put_char(x+0,y+7, ord("*"),tcod.BKGND_DEFAULT)
	console.put_char(x+1,y+7, drawval.CHARS["gold"]+64,tcod.BKGND_DEFAULT)
	console.put_char(x+2,y+7, ord("*"),tcod.BKGND_DEFAULT)
	console.fg[x][y+7] = drawval.COLORS["map-red"]
	console.fg[x+1][y+7] = drawval.COLORS["map-red"]
	console.fg[x+2][y+7] = drawval.COLORS["map-red"]
	console.print(x+4,y+7,"Gold!",drawval.COLORS["white"],drawval.COLORS["black"],tcod.BKGND_DEFAULT,tcod.LEFT)

	i_to_display = cx.SETTINGS[0]["sel"]

	console.print(x,y+10,"Controls",drawval.COLORS["white"],drawval.COLORS["black"],tcod.BKGND_DEFAULT,tcod.LEFT)
	
	console.print(x,y+23,"R: Reset",drawval.COLORS["white"],drawval.COLORS["black"],tcod.BKGND_DEFAULT,tcod.LEFT)
	console.print(x,y+25,"ESC: Quit",drawval.COLORS["white"],drawval.COLORS["black"],tcod.BKGND_DEFAULT,tcod.LEFT)
	
	console.print(x,y+15,cx.INPUT_SEL[i_to_display],drawval.COLORS["white"],drawval.COLORS["black"],tcod.BKGND_DEFAULT,tcod.LEFT)

def messageprint(z,s,m):
	z.clear(32,drawval.COLORS["white"],drawval.COLORS["black"])
	s = "> " + s
	if len(s) > z.width:

		mms = []
		while ((s.rfind(" ",0,(z.width-1)) != -1) and (len(s) > z.width)):
			dex = s.rfind(" ",0,(z.width+1))
			mms.append(s[0:(dex)])
			s = s[(dex+1):(len(s))]
		mms.append(s)
		
		for ms in mms:
			m.append(ms)
	else:
		m.append(s)
	for x in range(0,z.height):
		if m[len(m)-1-x] != "":
			#z.print(0,z.height-1-x,m[len(m)-1-x],drawval.COLORS["white"],drawval.COLORS["black"],tcod.BKGND_DEFAULT,tcod.LEFT)
			xl = 0
			for c in m[len(m)-1-x]:
				z.put_char(xl,z.height-1-x,ord(c),tcod.BKGND_DEFAULT)
				xl+=1
		
#message construction for basic actions

def construct_message(
	self,		#entity acting
	other,		#entity acted on
	verb_2p,	#2nd-person verb (w/ spaces)
	verb_3p,	#3rd-person verb (w/ spaces)
	act_ext="", #extended description e.g. "for 10 [damage/healing/etc]"
	val_ins=0,	#value to insert e.g. the 10
	unit="",	#unit for value (e.g. "HP" for healing)
	s_end=".",	#ends sentence
	shortmsg=False
	):

	if (self == other and self == "You"):
		return ""

	if self.dispname == "You":
		msg = "You" + verb_2p
	else:
		if self.dispname == "":
			msg = "The " + self.faction.name + verb_3p
		else:
			msg = self.dispname + verb_3p
	if shortmsg == False:
		if other.dispname =="":
			msg += "the " + self.faction.name
		else:
			msg += other.dispname
		if act_ext != "":
			msg += act_ext + str(val_ins) + unit
	msg +=s_end
	return msg