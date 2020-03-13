import constants as cx
from random import randint
import copy
import drawval
import entity as ec

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
	
	def walls_around_rand(self,x,y,walkable_map,player_floor):
		for z in range(0,9):
			x2 = (x-1)+(z%3)
			y2 = (y-1)+(z//3)
			if x2 > -1 and x2 < self.width and y2 > -1 and y2 < self.height and (walkable_map[x2][y2] == True):
				self.t_[x][y] = Tile(cx.TERRAIN["wall"])
				return
		if randint(0,1+player_floor) < 4:
			if randint(0,1+player_floor*2) < 4:
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

		for y in range(self.height):
			for x in range(self.width):
				z = self.t_[x][y].type
				paper_map.t_[x][y] = Tile(cx.TERRAIN[z])
				paper_map.t_[x][y].fg = drawval.COLORS["map-black"]
				paper_map.t_[x][y].bg = drawval.COLORS["map-white"]

		for y in range(self.height):
			for x in range(self.width):
				if self.t_[x][y].type in ("wall","solidwall"):
					if randint(0,(player_floor+4)) > 5:
						if randint(0,2) > 0:
							self.t_[x][y] = Tile(cx.TERRAIN["pit"])
						else:
							self.t_[x][y] = Tile(cx.TERRAIN["floor"])
	
		for y in range(self.height):
			for x in range(self.width):
				if self.t_[x][y].type in ("wall","solidwall") and randint(0,player_floor) > 3:
					self.t_[x][y] = Tile(cx.TERRAIN["floor"])

		walkable_map = self.walk_map(walkpairs)

		for y in range(self.height):
			for x in range(self.width):
				if self.t_[x][y].type in ("wall","solidwall"):
					self.walls_around_rand(x,y,walkable_map,player_floor)
	
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

	def draw_square(self,x0,y0,w,h,line_type="wall",fill_type=""):
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
	
def make_map(map,entities,G_TRAP_CHARS,player_floor):
	x0,x1 = 5, 5
	y0,y1 = 7, 7
	w0,w1 = 5, 7
	h0,h1 = 5, 7
	
	xw = 4
	rw = 6
	xh = 4
	rh = 6
	for y in range(rh+2,map.height-rh,xh+rh):
		for x in range(rw+2,map.width-rw,xw+rw):
			map.draw_square(x,y,xw-1,xh-1,"wall","wall")
			zrand = randint(0,3)
			zh = 6
			zw = 6
			map.draw_square(x-rw,y,rw-1,xh-1,"wall","wall")
			map.draw_square(x+xw,y,rw-1,xh-1,"wall","wall")
			map.draw_square(x,y-rh,xw-1,rh-1,"wall","wall")
			map.draw_square(x,y+xh,xw-1,rh-1,"wall","wall")
			if zrand != 0: #right
				zzrand = randint(x+xw+1,x+xw+rw-3)
				map.line_from(zzrand,zzrand,y,y+xh,"floor")
			if zrand != 1: #left
				zzrand = randint(x-rw+1,x-2)
				map.line_from(zzrand,zzrand,y,y+xh,"floor")
			if zrand != 2: #up
				zzrand = randint(y-rh+1,y-2)
				map.line_from(x,x+xw,zzrand,zzrand,"floor")
			if zrand != 3: #down
				zzrand = randint(y+xh+1,y+xh+rh-3)
				map.line_from(x,x+xw,zzrand,zzrand,"floor")

	for y in range(2,map.height-rh,xh+rh):
		for x in range(2,map.width-rw,xw+rw):
			zzrand = randint(0,8)
			if (zzrand % 3) == 1:
				map.t_[x][y] = Tile(cx.TERRAIN["wall"])
				map.t_[x+5][y] = Tile(cx.TERRAIN["wall"])
				map.t_[x][y+5] = Tile(cx.TERRAIN["wall"])
				map.t_[x+5][y+5] = Tile(cx.TERRAIN["wall"])
			if zzrand == 1:
				map.draw_square(x+1,y+1,3,3,"pit","wall")
			if zzrand == 2:
				map.draw_square(x+1,y+1,3,3,"pit","floor")
			if zzrand == 3:
				map.draw_square(x+2,y+2,1,1,"wall","solidwall")
			if zzrand == 4:
				map.draw_square(x+1,y+1,3,3,"pit","pit")
			if zzrand == 5:
				map.draw_square(x+1,y+1,3,3,"wall","wall")
			if zzrand == 6:
				for c in range(0,8):
					zrand2 = randint(1,4)
					zrand3= randint(1,4)
					map.t_[x+zrand2][y+zrand3] = Tile(cx.TERRAIN["pit"])
			if zzrand == 7:
				for c in range(0,8):
					zrand2 = randint(1,4)
					zrand3= randint(1,4)
					map.t_[x+zrand2][y+zrand3] = Tile(cx.TERRAIN["wall"])
			if zzrand == 8:
				for c in range(0,8):
					zrand2 = randint(1,4)
					zrand3 = randint(1,4)
					zrand4 = randint(0,1)
					if zrand4 == 0:
						map.t_[x+zrand2][y+zrand3] = Tile(cx.TERRAIN["wall"])
					else:
						map.t_[x+zrand2][y+zrand3] = Tile(cx.TERRAIN["pit"])
			if zzrand in (1,2,4):
				if randint(0,4) > 1:
					for zdoub in ((x+1,y),(x,y+1),(x+1,y+5),(x,y+4), (x+5,y+1),(x+4,y),(x+4,y+5),(x+5,y+4)):
						map.t_[zdoub[0]][zdoub[1]] = Tile(cx.TERRAIN["wall"])

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
			fg = "pit-fg",
			bg = "pit-bg",
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
	
	paper_map = Map(map.width,map.height)
	
	map.walls_to_other(player_floor,paper_map)
	map.walls_and_pits()

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