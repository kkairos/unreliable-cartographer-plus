import tcod, tcod.event
from controls import key_input
import entity as ec
import render as re
import constants as cx
import drawval
import map
from time import sleep
from random import randint, shuffle

def new_level(map_w,map_h,entities,G_TRAP_CHARS,G_GLYPH_CHARS,player_floor=1):
	level_map = map.Map(map_w,map_h)
	map.make_map(level_map,entities,G_TRAP_CHARS,player_floor)
	paper_map = map.Map(map_w,map_h)
	for y in range(map_h):
		for x in range(map_w):
			z = level_map.t_[x][y].type
			paper_map.t_[x][y] = map.newtile(cx.TERRAIN[z])
			paper_map.t_[x][y].fg = drawval.COLORS["map-black"]
			paper_map.t_[x][y].bg = drawval.COLORS["map-white"]

	paper_map.walls_and_pits()
	
	for y in range(map_h):
		for x in range(map_w):
			if paper_map.t_[x][y].type == "wall":
				paper_map.t_[x][y].char += 64
			if paper_map.t_[x][y].type == "pit":
				paper_map.t_[x][y].fg = drawval.COLORS["map-black"]
				paper_map.t_[x][y].bg = drawval.COLORS["map-white"]
				paper_map.t_[x][y].char += 64
			if paper_map.t_[x][y].type == "floor":
				paper_map.t_[x][y].char = 32
			if paper_map.t_[x][y].type == "solidwall":
				paper_map.t_[x][y].char = 32
				paper_map.t_[x][y].fg = drawval.COLORS["map-white"]
				paper_map.t_[x][y].bg = drawval.COLORS["map-white"]
			for entity in entities:
				RAND_CHARS = [drawval.CHARS["gold"]]
				RAND_CHARS.extend(G_GLYPH_CHARS)
				if ((entity.x == x) and (entity.y == y) and entity.istrap):
					if entity.dispname not in ("gold","Boulder","stairs","artifact"):
						paper_map.t_[x][y].char = G_GLYPH_CHARS[entity.traptype]
						paper_map.t_[x][y].fg = drawval.COLORS["map-red"]
						paper_map.t_[x][y].type = "trap"
					elif entity.dispname == "gold":
						paper_map.t_[x][y].char = drawval.CHARS["gold"]
						paper_map.t_[x][y].fg = drawval.COLORS["map-red"]
					elif entity.dispname == "stairs":
						paper_map.t_[x][y].char = drawval.CHARS["stairs"]
						paper_map.t_[x][y].fg = drawval.COLORS["map-green"]
					elif entity.dispname == "artifact":
						paper_map.t_[x][y].char = drawval.CHARS["artifact"]
						paper_map.t_[x][y].fg = drawval.COLORS["map-green"]
					if player_floor > 1:
						if entity.dispname not in ("stairs","artifact"):
							zrand = randint(0,len(RAND_CHARS)-1)
							paper_map.t_[x][y].char = RAND_CHARS[zrand]
	
	return level_map, paper_map

def draw_loop(player, level_map, paper_map, map_console, main_console, message_console,status_console,entities,player_state):
	fov = player.fov(level_map,entities)
	re.draw_map(level_map, paper_map, map_console, fov)
	re.draw_all(level_map,map_console,entities,fov)
	re.draw_con(main_console,map_console,main_console.width-map_console.width,0)
	re.draw_con(main_console,status_console,0,0)
	re.draw_con(main_console,message_console,status_console.width,main_console.height-message_console.height)
	tcod.console_flush()
	re.clear_all(level_map,map_console,entities)
	
def status_con(console,x,y,player_floor,player_gold):
	console.print(x,y,"Gold:  " + str(player_gold),drawval.COLORS["gold-fg"],drawval.COLORS[0],tcod.BKGND_DEFAULT,tcod.LEFT)
	console.print(x,y+1,"Floor: " + str(player_floor),drawval.COLORS[15],drawval.COLORS[0],tcod.BKGND_DEFAULT,tcod.LEFT)

def main():

	#basic screen setup
	
	screen_width = 80
	screen_height = 45
	map_w = 60
	map_h = 40
	
	map_console_w = 60
	map_console_h = 40

	#tcod events setup

	key = tcod.Key()
	mouse = tcod.Mouse()
	
	#create player and put player in entities array

	player = ec.Entity(4,2,drawval.CHARS["person"],15,0,10,10,cx.Faction.Ally,cx.DrawOrder.PLAYER,True,"You")
	entities = [player]

	player_state = 1	#player is alive
	
	player_gold = 0
	player_floor = 1

	# get and shuffle trap chars. 4 for floor tiles, and 4 for map glyphs
	
	G_TEMP_CHARS = drawval.TRAP_CHARS
	
	shuffle(G_TEMP_CHARS)
	
	G_TRAP_CHARS = G_TEMP_CHARS[0:4]
	G_GLYPH_CHARS = G_TEMP_CHARS[4:8]
	for x in range(0,len(G_GLYPH_CHARS)):
		G_GLYPH_CHARS[x]+=64


	#create new level map

	level_map, paper_map = new_level(map_w,map_h,entities,G_TRAP_CHARS,G_GLYPH_CHARS)
	
	tcod.console_set_custom_font(cx.FONT_FILE[cx.SETTINGS[1]["sel"]],
		tcod.FONT_TYPE_GRAYSCALE | tcod.FONT_LAYOUT_ASCII_INROW,
		32,16
		)
	main_console = tcod.console_init_root(screen_width, screen_height, "The Unreliable Cartographer", False, 3, "F", True)
	
	map_console = tcod.console.Console(map_console_w, map_console_h, "F", None)
	
	message_console = tcod.console.Console(map_console.width,main_console.height-map_console.height)
	
	status_console = tcod.console.Console(main_console.width-map_console.width,main_console.height,"F",None)
	status_console.print(status_console.width//2,1,"The Unreliable\nCartographer",drawval.COLORS[15],drawval.COLORS[0],tcod.BKGND_DEFAULT,tcod.CENTER)
	re.legend_print(status_console,G_GLYPH_CHARS,1,4)
	
	messages = []
	
	for x in range(0,message_console.height):
		messages.append("")
	
	welcome_message = "Welcome to *The Unreliable Cartographer.* This is a game about exploring ancient ruins to find an ancient artifact with a map of increasingly dubious accuracy and dodging traps along the way. Controls are on the left panel. We hope you like it!"
	re.messageprint(message_console, welcome_message, messages )
	
	fg_sh = 15
	bg_sh = 0

	fov = player.fov(level_map,entities)
	
	jump_trigger = False
	no_enemies = False
	quit_trigger = False
	new_floor = False
	reset_trigger = False
	
	fov = player.fov(level_map,entities)
	re.draw_paper_map(paper_map, map_console)
	
	while True:
	
		draw_loop(player, level_map, paper_map, map_console, main_console, message_console,status_console,entities,player_state)
		status_con(status_console,2,status_console.height-2,player_floor,player_gold)
		for event in tcod.event.wait():
			if event.type == "KEYDOWN":
				action = key_input(event.sym)
				
				#pause = False
				move = action.get('move')
				exit = action.get('exit')
				pause = action.get('pause')
				jump = action.get('jump')
				controlchange = action.get('controlchange')
				greset = action.get('reset')
				if player_state == 1:
					if move:
						dx,dy = move
						if not jump_trigger:
							player.move(dx,dy,level_map,entities,map_console,message_console,messages)
						elif jump_trigger:
							for z in range(0,2):
								if player.jump(dx,dy,level_map,entities,map_console,message_console,messages) == False:
									break
								else:
									draw_loop(player, level_map, paper_map, map_console, main_console, message_console,status_console,entities,player_state)
									sleep(0.0080)
							jump_trigger = False
						player.lastx = dx
						player.lasty = dy
						quit_trigger = False
						reset_trigger = False
					if jump:
						if not jump_trigger:
							re.messageprint(message_console, "Press [DIR] to jump 2 squares away in a direction, any other key to cancel.", messages )
							jump_trigger = True
							no_enemies = True
						elif jump_trigger:		
							re.messageprint(message_console, "Jump cancelled.", messages )
							jump_trigger = False
							no_enemies = True
						quit_trigger = False
						reset_trigger = False
					player_gold = player.istrapped(level_map,entities,map_console,message_console,messages,player_gold)
					if not no_enemies:
						for entity in entities:
							if entity.dispname == "Boulder":
								entity.move(entity.persistent_x,entity.persistent_y,level_map,entities,map_console,message_console,messages)
						for entity in entities:
							if entity.istrap and entity.trapstate > 0:
								entity.do_trap(level_map,paper_map,main_console,map_console,fov,message_console,messages,entities)
								if entity.dispname == "gold":
									entities.remove(entity)
								if entity.dispname == "stairs":
									new_floor = True
								if entity.dispname == "artifact":
									player_state = 0
					elif no_enemies:
						no_enemies = False

					if level_map.t_[player.x][player.y].type == "pit":
						fov = player.fov(level_map,entities)
						for z in drawval.CHARS["person_fall"]:
							player.char = z
							draw_loop(player, level_map, paper_map, map_console, main_console, message_console,status_console,entities,player_state)
						player_state = 0
						entities.remove(player)
						re.messageprint(message_console,"Oh, dear! You've fallen down a pit!",messages)

					if player.stats.hp < 1:
						player_state = 0
					status_con(status_console,2,status_console.height-2,player_floor,player_gold)
				if exit:
					if quit_trigger == False:
						re.messageprint(message_console, "Quit? [ESC] for 'Yes' or anything else for 'no'.", messages )
						no_enemies = True
						quit_trigger = True
						reset_trigger = False
					elif quit_trigger:
						return True
				if greset:
					if reset_trigger == False:
						re.messageprint(message_console, "Reset game? [R/r] for 'Yes' or anything else for 'no'.", messages )
						no_enemies = True
						reset_trigger = True
					elif reset_trigger:
						reset_trigger = False
						entities.clear()
						level_map.t_.clear()
						paper_map.t_.clear()
					
						player = ec.Entity(4,2,drawval.CHARS["person"],15,0,10,10,cx.Faction.Ally,cx.DrawOrder.PLAYER,True,"You")
						
						entities = [player]
						
						player_gold = 0
						player_floor = 1
						player.x = 4
						player.y = 2
						
						map_console.clear(15,drawval.COLORS["black"],)
						level_map, paper_map = new_level(map_w,map_h,entities,G_TRAP_CHARS,G_GLYPH_CHARS,player_floor)
						new_floor = False
						re.draw_paper_map(paper_map, map_console)
						fov = player.fov(level_map,entities)
						status_con(status_console,2,status_console.height-2,player_floor,player_gold)
						messages.extend(["","","","",""])
						re.messageprint(message_console, "Game has been reset!", messages )
						player_state = 1
				if controlchange:
					no_enemies = True
					cx.SETTINGS[0]["sel"] = (cx.SETTINGS[0]["sel"] + 1)% 3
					re.legend_print(status_console,G_GLYPH_CHARS,1,4)
					quit_trigger = False
					reset_trigger = False
					re.messageprint(message_console, "Changed controls to " + cx.INPUT_SEL_NAME[cx.SETTINGS[0]["sel"]] + ".", messages )

			elif event.type == "WINDOWCLOSE":
				return True
			
		if new_floor:

			entities.clear()
			level_map.t_.clear()
			paper_map.t_.clear()
		
			player = ec.Entity(4,2,drawval.CHARS["person"],15,0,10,10,cx.Faction.Ally,cx.DrawOrder.PLAYER,True,"You")
			
			entities = [player]
			
			player_floor += 1
			player.x = 4
			player.y = 2
			
			map_console.clear()
			level_map, paper_map = new_level(map_w,map_h,entities,G_TRAP_CHARS,G_GLYPH_CHARS,player_floor)
			new_floor = False
			re.draw_paper_map(paper_map, map_console)
			fov = player.fov(level_map,entities)
			status_con(status_console,2,status_console.height-2,player_floor,player_gold)

if __name__ == "__main__":
	main()