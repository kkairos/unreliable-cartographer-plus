import constants as cx
import render as re
from math import atan, pi
import tcod.event
import random
from drawval import CHARS, COLORS
import map as mp
from random import randint, choice
from time import sleep

class Stats:

	def __init__(self,hp, at=3, df=0):
		self.hp = hp
		self.max_hp = hp
		self.at = at
		self.df = df

class Entity:

	def __init__(self,
			x,y,
			char_input = 2,
			fg = "white",bg = "black",
			hp = 1,
			faction = cx.Faction.Enemy,
			draw_order = cx.DrawOrder.NPC,
			block_m = True,
			dispname = ""):
		self.x = x
		self.y = y
		self.char = char_input
		self.fg = fg
		self.bg = bg
		self.stats = Stats(hp)
		self.block_m = block_m
		self.block_j = block_m
		self.block_s = False
		self.faction = faction
		self.dispname = dispname
		self.draw_order = draw_order
		self.sightrange = 10
		self.istrap = False
		self.traptype = -1
		self.trapstate = 0

	def move(self,dx,dy,map,entities,map_console,message_console,messages,returnval=False):
		if (self.x+dx > -1 and self.x+dx < map.width and self.y+dy > -1 and self.y+dy < map.height):
			
			target_entity = blocking_entity(entities,self.x+dx,self.y+dy)
			if target_entity is not None and target_entity.faction != self.faction:
				self.attack(target_entity,message_console,messages)
				if returnval:
					return True
			elif map.t_[self.x+dx][self.y+dy].block_m:
				if (returnval and map.t_[self.x+dx][self.y+dy].type != "pit") or not returnval:
					if self.dispname == "Boulder" and map.t_[self.x+dx][self.y+dy].type == "pit":
						self.x+=dx
						self.y+=dy
						self.stats.hp == 0
						self.char == ord(" ")
						map.t_[self.x][self.y] = mp.Tile(cx.TERRAIN["floor"])
						map.walls_and_pits()
						entities.remove(self)
						re.messageprint(message_console,"The boulder filled in a pit!",messages)
					else:
						if self.dispname != "Boulder":
							message = "A " + map.t_[self.x+dx][self.y+dy].type + " blocks your way."
							re.messageprint(message_console,message,messages)
					if returnval:
						return True
				else:
					self.x+=dx
					self.y+=dy
					if returnval:
						return True

			else:
				self.x+=dx
				self.y+=dy
				if returnval:
					return False

	def jump(self,dx,dy,map,entities,map_console,message_console,messages):
		if (self.x+dx > -1 and self.x+dx < map.width and self.y+dy > -1 and self.y+dy < map.height):
			target_entity = blocking_entity(entities,self.x+dx,self.y+dy)
			if map.t_[self.x+dx][self.y+dy].block_j:
				re.messageprint(message_console,"*THUD*",messages)
				return False
			if target_entity is not None and target_entity.block_j:
				re.messageprint(message_console,"*THUD*",messages)
				return False
			else:
				self.x+=dx
				self.y+=dy
				return True

	def istrapped(self,map,entities,map_console,message_console,messages,player_gold):
		trap_entity = trap_at(entities,self.x,self.y)
		if (trap_entity is not None):
			if trap_entity.trapstate == 0:
				if trap_entity.dispname not in ["gold","stairs","artifact"]:
					trap_entity.trapstate = 1
					message = re.construct_message(self,trap_entity," trigger the "," triggers the ","",0,unit="",s_end=" trap!",shortmsg=False)
					re.messageprint(message_console,message,messages)

				else:
					if trap_entity.dispname == "gold":
						trap_entity.trapstate = 1
						grand = randint(8,32)
						message ="You collect " + str(grand) + chr(CHARS["gold"]) + "!"
						if grand % 7 == 2:
							message = "You trigger the Gold trap! (Just kidding! " + message + ")"
						re.messageprint(message_console,message,messages)
						player_gold += grand
					elif trap_entity.dispname == "stairs":
						trap_entity.trapstate = 1
						message = "You go down the stairs!"
						re.messageprint(message_console,message,messages)
					elif trap_entity.dispname == "artifact":
						trap_entity.trapstate = 1
						message = "You got the artifact! +2500 gold! You have won the game!"
						player_gold += 2500
						re.messageprint(message_console,message,messages)

		return player_gold
	
	def do_trap(self,map,paper_map,main_console,map_console,fov,message_console,messages,entities):
		trap_type = self.traptype
		if trap_type == 0:
			radius = 2
			for z in CHARS["floor_give"]:
				lc=0
				for x in range(self.x-radius,self.x+radius+1):
					for y in (self.y+lc,self.y-lc):
						if x > -1 and x < map.width and y > -1 and y < map.height:
							if map.t_[x][y].type == "floor":
								map.t_[x][y].char = z
								map.t_[x][y].fg = COLORS["floor-bg"]
								map.t_[x][y].bg = COLORS["pit-bg"]
					if x < self.x:
						lc+=1
					if x > self.x-1:
						lc-=1

				fov = entities[0].fov(map,entities)
				re.draw_map(map, paper_map, map_console, fov)
				re.draw_all(map,map_console,entities,fov)
				re.draw_con(main_console,map_console,main_console.width-map_console.width,0)
				re.draw_con(main_console,message_console,main_console.width-map_console.width,main_console.height-message_console.height)
				tcod.console_flush()
				re.clear_all(map,map_console,entities)
				sleep(0.050)

			lc=0
			for x in range(self.x-radius,self.x+radius+1):
				for y in (self.y+lc,self.y-lc):
					if x > -1 and x < map.width and y > -1 and y < map.height:
						if map.t_[x][y].type == "floor":
							map.t_[x][y] = mp.Tile(cx.TERRAIN["pit"])
				if x < self.x:
					lc+=1
				if x > self.x-1:
					lc-=1
			map.walls_and_pits()
		
		elif trap_type == 1:
			fov = entities[0].fov(map,entities)
			re.draw_map(map, paper_map, map_console, fov)
			re.draw_all(map,map_console,entities,fov)
			re.draw_con(main_console,map_console,main_console.width-map_console.width,0)
			re.draw_con(main_console,message_console,main_console.width-map_console.width,main_console.height-message_console.height)
			tcod.console_flush()
			re.clear_all(map,map_console,entities)
			sleep(0.080)
			trapeffect_blocked = False
			while trapeffect_blocked == False:
				trapeffect_blocked = entities[0].move(entities[0].lastx,entities[0].lasty,map,entities,map_console,message_console,messages,True)
				fov = entities[0].fov(map,entities)
				re.draw_map(map, paper_map, map_console, fov)
				re.draw_all(map,map_console,entities,fov)
				re.draw_con(main_console,map_console,main_console.width-map_console.width,0)
				re.draw_con(main_console,message_console,main_console.width-map_console.width,main_console.height-message_console.height)
				tcod.console_flush()
				re.clear_all(map,map_console,entities)
				sleep(0.0075)

		elif trap_type == 2:
			fov = entities[0].fov(map,entities)
			re.draw_map(map, paper_map, map_console, fov)
			re.draw_all(map,map_console,entities,fov)
			re.draw_con(main_console,map_console,main_console.width-map_console.width,0)
			re.draw_con(main_console,message_console,main_console.width-map_console.width,main_console.height-message_console.height)
			tcod.console_flush()
			re.clear_all(map,map_console,entities)
			sleep(0.080)
			entities[0].lastx = entities[0].lastx*-1
			entities[0].lasty = entities[0].lasty*-1
			trapeffect_blocked = False
			while trapeffect_blocked == False:
				trapeffect_blocked = entities[0].move(entities[0].lastx,entities[0].lasty,map,entities,map_console,message_console,messages,True)
				fov = entities[0].fov(map,entities)
				re.draw_map(map, paper_map, map_console, fov)
				re.draw_all(map,map_console,entities,fov)
				re.draw_con(main_console,map_console,main_console.width-map_console.width,0)
				re.draw_con(main_console,message_console,main_console.width-map_console.width,main_console.height-message_console.height)
				tcod.console_flush()
				re.clear_all(map,map_console,entities)
				sleep(0.0075)
		
		elif trap_type == 3:

			px = randint(-1,1)
			if px == 0:
				py = randint(-1,1)
			else:
				py = 0
			tries = 0
			while map.t_[self.x+px][self.y+py].type != "floor":
				randz = randint(0,4)
				if randz == 0:
					px=1
					py=0
				elif randz ==1:
					px=-1
					py=0
				elif randz ==2:
					px=0
					py=-1
				elif randz ==3:
					px=0
					py=1
				tries +=1
				if tries > 100:
					map.t_[self.x+px][self.y+py] = mp.Tile(cx.TERRAIN["floor"])
					map.walls_and_pits()
			
			boulder = Entity(
				self.x+px,self.y+py,
				char_input = CHARS["boulder"],
				fg = "boulder-fg",
				bg = cx.TERRAIN["floor"]["bg"],
				hp = 1,
				faction = cx.Faction.Enemy,
				draw_order = cx.DrawOrder.NPC,
				block_m = True,
				dispname = "Boulder")
			boulder.persistent_x = px*-1
			boulder.persistent_y = py*-1
			entities.append(boulder)
			boulder.block_j = False
			boulder.block_s = True
			boulder.stats.at = 100
			boulder.stats.df = 3
			fov = entities[0].fov(map,entities)
			re.draw_map(map, paper_map, map_console, fov)
			re.draw_all(map,map_console,entities,fov)
			re.draw_con(main_console,map_console,main_console.width-map_console.width,0)
			re.draw_con(main_console,message_console,main_console.width-map_console.width,main_console.height-message_console.height)
			tcod.console_flush()
			re.clear_all(map,map_console,entities)
			sleep(0.080)

		self.trapstate = -1
		for event in tcod.event.wait(0.5):
			return
		
	def attack(self,other,message_console,messages,dx=0,dy=0):
	
		damage = self.stats.at - other.stats.df
		message = re.construct_message(self,other," attack ", " attacks "," for ",damage," HP")
		other.stats.hp -= damage
		if other.stats.hp < 1:
			message += " " + re.construct_message(other,other," die"," dies","",0,"","!",True)
			other.block_m = False
			other.char = ord("%")
			other.draw_order = cx.DrawOrder.FLOOR
			self.x+=dx
			self.y+=dy

		if message != "":
			re.messageprint(message_console,message,messages)
	
	def fov(self,map,entities):
	
		fov = [[float(0.0) for y in range(map.height)] for x in range(map.width)]
		eblock = [[False for y in range(map.height)] for x in range(map.width)]
		
		for y in range(map.height):
			for x in range(map.width):
				fov[x][y] = False
				eblock[x][y] = False

		radius = self.sightrange
		
		for en in entities:
			if (en.block_s == True) and (en != self):
				eblock[en.x][en.y] = True

		for theta in range(len(cx.THETAS)):
			
			xd_i, yd_i = float(self.x+0.5), float(self.y+0.5)
			xd_d, yd_d = cx.THETAS[theta]
			fov[self.x][self.y] = 1
			map.t_[self.x][self.y].explored = True

			for r in range(radius):
				xd_i+=xd_d
				yd_i+=yd_d
				if (int(xd_i) < 0) or (int(yd_i) < 0) or (int(xd_i) > map.width-1) or (int(yd_i) > map.height-1):
					break
				if r == 0 or ((int(xd_i) == self.x) and (int(yd_i) == self.y)):
					fov[int(xd_i)][int(yd_i)] = float(1.0)
				else:
					fov[int(xd_i)][int(yd_i)] = float(-1.4*atan((r-2)/2)/pi+0.6)
				map.t_[int(xd_i)][int(yd_i)].explored = True
				if map.t_[int(xd_i)][int(yd_i)].block_s or eblock[int(xd_i)][int(yd_i)]:
					break
		return fov
	
def blocking_entity(entities,x,y):
	for entity in entities:
		if ((entity.x == x) and (entity.y == y) and entity.block_m):
			return entity
	return None

def trap_at(entities,x,y):
	for entity in entities:
		if ((entity.x == x) and (entity.y == y) and entity.istrap):
			return entity
	return None