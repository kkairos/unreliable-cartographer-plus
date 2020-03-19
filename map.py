import constants as cx
from random import randint
import copy
import drawval
import entity as ec
from controls import key_input
import tcod, tcod.event
from time import sleep

class Tile:

	def __init__(self,terrain):
		self.block_m = terrain["block_m"]
		if terrain["block_s"] is None:
			self.block_s = terrain["block_m"]
		else:
			self.block_s = terrain["block_s"] 
		self.block_j = terrain["block_j"]
		self.char = terrain["char"]
		self.fg = drawval.COLORS[terrain["fg"]]
		self.bg = drawval.COLORS[terrain["bg"]]
		self.explored = False
		self.type = terrain["type"]
		self.lastx = 0
		self.lasty = 0

class Map:

	def __init__(self,width,height):
		self.width = width
		self.height = height
		self.t_ = self.t_init()
		
	def t_init(self):
		tiles = [[Tile(cx.TERRAIN["wall"]) for y in range(self.height)] for x in range(self.width)]

		map_debug = 0
		
		for y in range(self.height):
			for x in range(self.width):
				tiles[x][y] = Tile(cx.TERRAIN["floor"])

		for y in range(self.height):
			for x in range(self.width):
				if y==1 or x==1 or (y==self.height-2) or (x==self.width-2):
					tiles[x][y] = Tile(cx.TERRAIN["wall"])
				if y==0 or x==0 or (y==self.height-1) or (x==self.width-1):
					tiles[x][y] = Tile(cx.TERRAIN["wall"])

		if map_debug == 1:
			for y in range(self.height):
				for x in range(self.width):
					tiles[x][y].explored = True
		return tiles

	def walls_around_reg(self,x,y,walkable_map,player_floor):
		for z in range(0,9):
			x2 = (x-1)+(z%3)
			y2 = (y-1)+(z//3)
			if x2 > -1 and x2 < self.width and y2 > -1 and y2 < self.height and (walkable_map[x2][y2] == True):
				return
		self.t_[x][y] = Tile(cx.TERRAIN["solidwall"])

	def walls_around_solidwall(self,x,y,walkable_map,player_floor):
		for z in range(0,9):
			x2 = (x-1)+(z%3)
			y2 = (y-1)+(z//3)
			if x2 > -1 and x2 < self.width and y2 > -1 and y2 < self.height and (walkable_map[x2][y2] == True):
				self.t_[x][y] = Tile(cx.TERRAIN["wall"])
				return
	
	def walls_around_rand(self,x,y,walkable_map,player_floor):
		for z in range(0,9):
			x2 = (x-1)+(z%3)
			y2 = (y-1)+(z//3)
			if x2 > -1 and x2 < self.width and y2 > -1 and y2 < self.height and (walkable_map[x2][y2] == True):
				self.t_[x][y] = Tile(cx.TERRAIN["wall"])
				return
		if randint(0,1+player_floor) < 4:
			if randint(0,1+player_floor*3) < 4:
				self.t_[x][y] = Tile(cx.TERRAIN["floor"])
			else:
				self.t_[x][y] = Tile(cx.TERRAIN["pit"])
	
	def walk_map(self,walkpairs):
		walkable_map = [[False for y in range(self.height)] for x in range(self.width)]
		
		while len(walkpairs) > 0:
			for xypair in walkpairs:
				x2,y2 = xypair
				walkable_map[x2][y2] = True
				for z in range(0,9):
					tmp_x = x2-1+(z%3)
					tmp_y = y2-1+(z//3)
					if tmp_x > -1 and tmp_y > -1 and tmp_x < self.width and tmp_y < self.height:
						if self.t_[tmp_x][tmp_y].type == "floor" and walkable_map[tmp_x][tmp_y] == False:
							walkpairs.append((tmp_x,tmp_y))
				
				walkpairs.remove(xypair)

		return walkable_map
	
	def walls_to_other(self,player_floor,paper_map):

		walkable_map = [[False for y in range(self.height)] for x in range(self.width)]
		walkpairs = []
		for y in range(self.height):
			for x in range(self.width):
				if self.t_[x][y].type in ("floor","pit"):
					walkable_map[x][y] = True
					walkpairs.append((x,y))

		for y in range(self.height):
			for x in range(self.width):
				if self.t_[x][y].type == "wall":
					self.walls_around_reg(x,y,walkable_map,player_floor)
				if self.t_[x][y].type == "solidwall":
					self.walls_around_solidwall(x,y,walkable_map,player_floor)

		for y in range(self.height):
			for x in range(self.width):
				z = self.t_[x][y].type
				paper_map.t_[x][y] = Tile(cx.TERRAIN[z])
				paper_map.t_[x][y].fg = drawval.COLORS["map-black"]
				paper_map.t_[x][y].bg = drawval.COLORS["map-white"]

		for y in range(self.height):
			for x in range(self.width):
				if self.t_[x][y].type in ("wall","solidwall"):
					if randint(0,(player_floor+8)) > 9:
						if randint(0,player_floor) > 0:
							self.t_[x][y] = Tile(cx.TERRAIN["pit"])
						else:
							self.t_[x][y] = Tile(cx.TERRAIN["floor"])
	
		for y in range(self.height):
			for x in range(self.width):
				if self.t_[x][y].type in ("wall","solidwall") and randint(0,player_floor) > 3:
					if randint(0,1+player_floor*3) < 4:
						self.t_[x][y] = Tile(cx.TERRAIN["floor"])
					else:
						self.t_[x][y] = Tile(cx.TERRAIN["pit"])

		walkable_map = self.walk_map(walkpairs)

		for y in range(self.height):
			for x in range(self.width):
				if self.t_[x][y].type in ("wall","solidwall"):
					self.walls_around_rand(x,y,walkable_map,player_floor)
					
		return walkable_map
	
	def walls_and_pits(self):
	
		for y in range(self.height):
			for x in range(self.width):
				if self.t_[x][y].type == "wall":
					z_tmp = 0
					z_tmp += self.char_update_val(x,y-1,1,"wall")
					z_tmp += self.char_update_val(x,y+1,2,"wall")
					z_tmp += self.char_update_val(x+1,y,4,"wall")
					z_tmp += self.char_update_val(x-1,y,8,"wall")
					self.t_[x][y].char = cx.walldraw[z_tmp]
				if self.t_[x][y].type == "pit":
					z_tmp = 0
					z_tmp += self.char_update_val(x-1,y-1,1,"pit")
					z_tmp += self.char_update_val(x,y-1,2,"pit")
					z_tmp += self.char_update_val(x-1,y,4,"pit")
					self.t_[x][y].char = cx.pitdraw[z_tmp]

	def char_update_val(self,x,y,v,type):
		if ((x < 0) or (x > (self.width -1))):
			return 0
		elif ((y < 0) or (y > (self.height -1))):
			return 0
		else:
			if ((type == "pit") and (self.t_[x][y].type != type)):
				return v
			elif ((type != "pit") and (self.t_[x][y].type == type)):
				return v
			else:
				return 0

	def line_from(self,x0,x1,y0,y1,line_type):
		if x0 == x1:
			self.line_v(y0,y1,x0,line_type)
		elif y0 == y1:
			self.line_h(x0,x1,y0,line_type)

	def line_h(self,x0,x1,y,line_type):
		for x in range(x0,x1+1):
			self.t_[x][y] = Tile(cx.TERRAIN[line_type])
			
	def line_v(self,y0,y1,x,line_type):
		for y in range(y0,y1+1):
			self.t_[x][y] = Tile(cx.TERRAIN[line_type])

	def draw_square(self,x,y,w,h,line_type="wall",fill_type=""):
		if fill_type != "":
			for z in range(x,x+w):
				self.line_from(z,z,y,y+h,fill_type)
		self.line_from(x,x+w,y,y,line_type)
		self.line_from(x,x+w,y+h,y+h,line_type)
		self.line_from(x,x,y,y+h,line_type)
		self.line_from(x+w,x+w,y,y+h,line_type)

	def old_draw_square(self,x0,y0,w,h,line_type="wall",fill_type=""):
		if fill_type != "":
			for x in range(x0,x0+w+1):
				self.line_from(x,x,y0,y0+h,fill_type)
		self.line_from(x0,x0+w,y0,y0,line_type)
		self.line_from(x0,x0+w,y0+h,y0+h,line_type)
		self.line_from(x0,x0,y0,y0+h,line_type)
		self.line_from(x0+w,x0+w,y0,y0+h,line_type)

	def draw_house(self,hx,hy,hw,hh):
		
		self.draw_square(hx,hy,hw,hh,"wall","wall")

def rand_square(x0,x1,y0,y1,w0,w1,h0,h1):

	rand_s_x, rand_s_y = randint(x0,x1), randint(y0,y1)
	rand_s_w, rand_s_h = randint(w0,w1), randint(h0,h1)
	
	return rand_s_x, rand_s_y, rand_s_w, rand_s_h

def divide_map(map,x,y,w,h,tiletype,defdivide):
	
	mapadds = []
	
	mapadds_tries = 0
	while len(mapadds) == 0 and mapadds_tries < 2:
		if defdivide or randint(0,12) > 0:
			divrand = randint(0,1)
			if divrand == 0 and w > 7:
				xrand = randint(x+3,x+w-3)
				mapadds.append([x,y,xrand-x,h])
				mapadds.append([xrand,y,x+w-xrand,h])
				if map.t_[xrand][y].type != "door" and map.t_[xrand][y+h].type != "door":
					map.line_from(xrand,xrand,y,y+h,tiletype)
					yrand = randint(y+1,y+h-1)
					map.t_[xrand][yrand] = Tile(cx.TERRAIN["door"])
			elif divrand == 1 and h > 7:
				yrand = randint(y+3,y+h-3)
				mapadds.append([x,y,w,yrand-y])
				mapadds.append([x,yrand,w,y+h-yrand])
				if map.t_[x][yrand].type != "door" and map.t_[x+w][yrand].type != "door":
					map.line_from(x,x+w,yrand,yrand,tiletype)
					xrand = randint(x+1,x+w-1)
					map.t_[xrand][yrand] = Tile(cx.TERRAIN["door"])
		mapadds_tries+=1
		
	return mapadds

def decorate_room(map,rx,ry,rw,rh):
	zrand = randint(0,1)
	if zrand == 0:
		map.draw_square(rx+1,ry+1,rw-2,rh-2,"floor","pit")
	if zrand == 1:
		map.draw_square(rx+2,ry+2,rw-4,rh-4,"wall","solidwall")
	if randint(0,1) == 0:
		map.t_[rx+1][ry+1] = Tile(cx.TERRAIN["pit"])
	if randint(0,1) == 1:
		map.t_[rx+rw-1][ry+1] = Tile(cx.TERRAIN["pit"])
	if randint(0,1) == 1:
		map.t_[rx+rw-1][ry+rh-1] = Tile(cx.TERRAIN["pit"])
	if randint(0,1) == 1:
		map.t_[rx+1][ry+rh-1] = Tile(cx.TERRAIN["pit"])

def make_map(map,entities,G_TRAP_CHARS,player_floor):

	map.draw_square(0,0,map.width-1,map.height-1,"wall","wall")
	map.draw_square(2,2,map.width-5,map.height-5,"wall","floor")

	regions = [[2,2,map.width-5,map.height-5]]
	
	z = 0
	div_limit = 100
	for region in regions:
		rx,ry,rw,rh = region
		if z < 3:
			mapadds = divide_map(map,rx,ry,rw,rh,"wall",True)
			if len(mapadds) == 0 and rw > 3 and rh > 3:
				decorate_room(map,rx,ry,rw,rh)
		else:
			mapadds = divide_map(map,rx,ry,rw,rh,"wall",False)
			if len(mapadds) == 0 and rw > 3 and rh > 3:
				decorate_room(map,rx,ry,rw,rh)
		z+=1
		if mapadds is not None:
			regions.extend(mapadds)
	
	z = 0

	for y in range(1,map.height-1):
		for x in range(1,map.width-1):
			if map.t_[x][y].type == "door":
				map.t_[x][y] = Tile(cx.TERRAIN["floor"])
			if map.t_[x][y].type == "wall":
				if randint(0,29) == 0:
					if map.t_[x-1][y].type == "wall" and map.t_[x+1][y].type == "wall":
						if map.t_[x][y-1].type != "wall" and map.t_[x][y+1].type != "wall":
							map.t_[x][y] = Tile(cx.TERRAIN["floor"])
					if map.t_[x][y-1].type == "wall" and map.t_[x][y+1].type == "wall":
						if map.t_[x-1][y].type != "wall" and map.t_[x+1][y].type != "wall":
							map.t_[x][y] = Tile(cx.TERRAIN["floor"])
	
	paper_map = Map(map.width,map.height)
	
	trapxys = []
	for z in range(0,(24+player_floor*12)):
		trap_type = z%4
		yrand = randint(2,map.height-3)
		xrand = randint(2,map.width-3)
		safedistval = 7
		distval = 5
		tries = 0
		while (map.t_[xrand][yrand].type != "floor" or distval < safedistval):
			yrand = randint(2,map.height-3)
			xrand = randint(2,map.width-3)

			distvals = []
			tries+=1
			for entity in entities:
				xa,ya = entity.x,entity.y
				distvals.append(abs(yrand-ya)+abs(xrand-xa))
			distval = min(distvals)
			if tries > 100 and entity_at_xy(entities,xrand,yrand) == False:
				distval = 8

		trapxys.append((xrand,yrand))
		trap = ec.Entity(
			xrand,yrand,
			char_input = G_TRAP_CHARS[trap_type],
			fg = "floor-trap-fg",
			bg = cx.TERRAIN["floor"]["bg"],
			hp = 1,
			faction = cx.Faction.Enemy,
			draw_order = cx.DrawOrder.FLOOR,
			block_m = False,
			dispname = cx.TRAPS[trap_type]["name"])
		trap.istrap = True
		trap.traptype = trap_type
		entities.append(trap)
		if trap.traptype == 0:
			lc = 0
			trap_remotes(map,trap.x,trap.y,2)

	tries = 0
	for z in range(0,(16+player_floor*16)):	
		yrand = randint(2,map.height-3)
		xrand = randint(2,map.width-3)
		while (map.t_[xrand][yrand].type != "floor") or entity_at_xy(entities,xrand,yrand) == True:
			yrand = randint(2,map.height-3)
			xrand = randint(2,map.width-3)
			tries+=1

		gold = ec.Entity(
			xrand,yrand,
			char_input = drawval.CHARS["gold"],
			fg = "gold-fg",
			bg = cx.TERRAIN["floor"]["bg"],
			hp = 1,
			faction = cx.Faction.Enemy,
			draw_order = cx.DrawOrder.FLOOR,
			block_m = False,
			dispname = "gold")
		gold.istrap = True
		entities.append(gold)

	trap_type = z%4
	yrand = randint(2,map.height-3)
	xrand = randint(2,map.width-3)
	safedistval = 18
	distval = 5
	tries = 0
	while (map.t_[xrand][yrand].type != "floor" or distval < safedistval):
		yrand = randint(2,map.height-3)
		xrand = randint(2,map.width-3)
		distvals = []
		tries+=1
		xa,ya = entities[0].x,entities[0].y
		distval = abs(yrand-ya)+abs(xrand-xa)
		if tries > 100:
			distval = 8
	if player_floor < 5:
		stairs = ec.Entity(
			xrand,yrand,
			char_input = drawval.CHARS["stairs"],
			fg = "stairs-fg",
			bg = "stairs-bg",
			hp = 1,
			faction = cx.Faction.Enemy,
			draw_order = cx.DrawOrder.FLOOR,
			block_m = False,
			dispname = "stairs")
		map.t_[xrand][yrand] = Tile(cx.TERRAIN["stairs"])
		stairs.istrap = True
		for entity in entities:
			if entity.x == stairs.x and entity.y ==stairs.y:
				entities.remove(entity)
		entities.append(stairs)
	else:
		artifact = ec.Entity(
			xrand,yrand,
			char_input = drawval.CHARS["artifact"],
			fg = "gold-fg",
			bg = "tile-bg",
			hp = 1,
			faction = cx.Faction.Enemy,
			draw_order = cx.DrawOrder.FLOOR,
			block_m = False,
			dispname = "artifact")
		artifact.istrap = True
		for entity in entities:
			if entity.x == artifact.x and entity.y ==artifact.y:
				entities.remove(entity)
		entities.append(artifact)

	walkable_map = map.walls_to_other(player_floor,paper_map)

	while True:
		xrand = randint(0,map.width-1)
		yrand = randint(0,map.height-1)
		print(xrand,yrand,walkable_map[xrand][yrand],map.t_[xrand][yrand].type)
		if walkable_map[xrand][yrand] == True and map.t_[xrand][yrand].type == "floor" and entity_at_xy(entities,xrand,yrand) == False:
			break

	entities[0].x = xrand
	entities[0].y = yrand
	
	map.walls_and_pits()
	paper_map.walls_and_pits()

	return paper_map

def entity_at_xy(entities,x,y):
	for entity in entities:
		if entity.x == x and entity.y == y:
			return True
	return False

def trap_remotes(map,trap_x,trap_y,radius):
	lc = 0
	for x in range(trap_x-radius,trap_x+radius+1):
		for y in (trap_y+lc,trap_y-lc):
			if x > -1 and x < map.width and y > -1 and y < map.height:
				map.t_[x][y].char = drawval.CHARS["remote_trap"]
		if x < trap_x:
			lc+=1
		if x > trap_x-1:
			lc-=1