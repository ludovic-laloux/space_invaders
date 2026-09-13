import pygame, sys
from player import Player
import obstacle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser
 
class Game:
	def __init__(self):
		# Player setup
		player_sprite = Player((screen_width / 2,screen_height),screen_width,5)
		self.player = pygame.sprite.GroupSingle(player_sprite)

		# health and score setup
		self.lives = 3
		self.live_surf = pygame.image.load('../graphics/player.png').convert_alpha()
		self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 10) - 10
		self.score = 0
		self.font = pygame.font.Font('../font/Pixeled.ttf',20)

		# Obstacle setup
		self.shape = obstacle.shape
		self.block_size = 6
		self.blocks = pygame.sprite.Group()
		self.obstacle_amount = 4
		self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
		self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = screen_width / 15, y_start = 480)

		# Alien setup
		self.aliens = pygame.sprite.Group()
		self.alien_lasers = pygame.sprite.Group()
		self.alien_setup(rows = 6, cols = 8)
		self.alien_direction = 1
		self.alien_speed = 1
		self.level = 1
		self.alien_laser_timer = 800

		# Extra setup
		self.extra = pygame.sprite.GroupSingle()
		self.extra_spawn_time = randint(40,80)

		# Audio
		self.music = pygame.mixer.Sound('../audio/music.wav')
		self.music.set_volume(0.2)
		self.laser_sound = pygame.mixer.Sound('../audio/laser.wav')
		self.laser_sound.set_volume(0.1)
		self.explosion_sound = pygame.mixer.Sound('../audio/explosion.wav')
		self.explosion_sound.set_volume(0.3)
		self.damage_sound = pygame.mixer.Sound("../audio/damage.wav")

		# UI setup
		self.paused = False
		self.game_over = False
		self.intro = True

	def create_obstacle(self, x_start, y_start,offset_x):
		for row_index, row in enumerate(self.shape):
			for col_index,col in enumerate(row):
				if col == 'x':
					x = x_start + col_index * self.block_size + offset_x
					y = y_start + row_index * self.block_size
					block = obstacle.Block(self.block_size,(241,79,80),x,y)
					self.blocks.add(block)

	def create_multiple_obstacles(self,*offset,x_start,y_start):
		for offset_x in offset:
			self.create_obstacle(x_start,y_start,offset_x)

	def alien_setup(self,rows,cols,x_distance = 60,y_distance = 48,x_offset = 70, y_offset = 100):
		for row_index, row in enumerate(range(rows)):
			for col_index, col in enumerate(range(cols)):
				x = col_index * x_distance + x_offset
				y = row_index * y_distance + y_offset
				
				if row_index == 0: alien_sprite = Alien('yellow',x,y)
				elif 1 <= row_index <= 2: alien_sprite = Alien('green',x,y)
				else: alien_sprite = Alien('red',x,y)
				self.aliens.add(alien_sprite)

	def alien_position_checker(self):
		all_aliens = self.aliens.sprites()
		for alien in all_aliens:
			if alien.rect.right >= screen_width:
				self.alien_direction = -1
				self.alien_move_down(2)
			elif alien.rect.left <= 0:
				self.alien_direction = 1
				self.alien_move_down(2)

	def alien_move_down(self,distance):
		if self.aliens:
			for alien in self.aliens.sprites():
				alien.rect.y += distance

	def alien_shoot(self):
		if self.aliens.sprites():
			random_alien = choice(self.aliens.sprites())
			laser_sprite = Laser(random_alien.rect.center,6,screen_height)
			self.alien_lasers.add(laser_sprite)
			self.laser_sound.play()

	def extra_alien_timer(self):
		self.extra_spawn_time -= 1
		if self.extra_spawn_time <= 0:
			self.extra.add(Extra(choice(['right','left']),screen_width))
			self.extra_spawn_time = randint(400,800)

	def collision_checks(self):

		# player lasers 
		if self.player.sprite.lasers:
			for laser in self.player.sprite.lasers:
				# obstacle collisions
				if pygame.sprite.spritecollide(laser,self.blocks,True):
					laser.kill()

				# alien collisions
				aliens_hit = pygame.sprite.spritecollide(laser,self.aliens,True)
				if aliens_hit:
					for alien in aliens_hit:
						self.score += alien.value
					laser.kill()
					self.explosion_sound.play()

				# extra collision
				if pygame.sprite.spritecollide(laser,self.extra,True):
					self.explosion_sound.play()
					self.score += 500
					laser.kill()

		# alien lasers 
		if self.alien_lasers:
			for laser in self.alien_lasers:
				# obstacle collisions
				if pygame.sprite.spritecollide(laser,self.blocks,True):
					laser.kill()

				# player collisions
				if pygame.sprite.spritecollide(laser,self.player,False):
					self.damage_sound.play()
					laser.kill()
					self.lives -= 1
					if self.lives <= 0:
						self.game_over = True
						game.music.stop()

		# aliens
		if self.aliens:
			for alien in self.aliens:
				pygame.sprite.spritecollide(alien,self.blocks,True)

				if pygame.sprite.spritecollide(alien,self.player,False):
					pygame.quit()
					sys.exit()
	
	def display_lives(self):
		for live in range(self.lives - 1):
			x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
			screen.blit(self.live_surf,(x,8))

	def display_score(self):
		score_surf = self.font.render(f'score: {self.score}',False,'white')
		score_rect = score_surf.get_rect(topleft = (10,-10))
		screen.blit(score_surf,score_rect)

	def victory_message(self):
		if not self.aliens.sprites():
			victory_font = pygame.font.Font("../font/pixeled.ttf",30)
			victory_surf = victory_font.render('You won',False,'white')
			victory_rect = victory_surf.get_rect(center = (screen_width / 2, screen_height / 2))
			screen.blit(victory_surf,victory_rect)

	def pause_menu(self):
		pause_surf = self.font.render("PAUSED",False,"white")
		pause_rect = pause_surf.get_rect(center = (screen_width/2,screen_height/2 - 30))
		screen.blit(pause_surf,pause_rect)

		resume_surf = self.font.render("Press Enter to resume",False,"white")
		resume_rect = resume_surf.get_rect(center = (screen_width/2,screen_height/2 + 30))
		screen.blit(resume_surf,resume_rect)

		quit_surf = self.font.render("Press Esc to quit",False,"white")
		quit_rect = quit_surf.get_rect(center = (screen_width/2,screen_height/2 + 90))
		screen.blit(quit_surf,quit_rect)

	def game_over_menu(self):
		game_over_surf = self.font.render("GAME OVER",False,"white")
		game_over_rect = game_over_surf.get_rect(center = (screen_width/2,screen_height/2 - 30))
		screen.blit(game_over_surf,game_over_rect)

		restart_surf = self.font.render("Press Enter to restart",False,"white")
		restart_rect = restart_surf.get_rect(center = (screen_width/2,screen_height/2 + 30))
		screen.blit(restart_surf,restart_rect)

		quit_surf = self.font.render("Press Esc to quit",False,"white")
		quit_rect = quit_surf.get_rect(center = (screen_width/2,screen_height/2 + 90))
		screen.blit(quit_surf,quit_rect)

	def intro_screen(self):
		logo_surf = pygame.image.load("../graphics/logo.jpg").convert_alpha()
		logo_surf = pygame.transform.scale(logo_surf,(screen_width,screen_height))
		logo_rect = logo_surf.get_rect(center = (screen_width/2,screen_height/2))
		screen.blit(logo_surf,logo_rect)

		start_surf = self.font.render("PRESS S TO START",False,"white")
		start_rect = start_surf.get_rect(center = (screen_width/2,screen_height/2 +260))
		screen.blit(start_surf,start_rect)

	def level_up(self):
		self.level += 1

		if self.level == 2:
			self.alien_speed = 2
			self.alien_laser_timer = 700

		elif self.level == 3:
			self.alien_speed = 3
			self.alien_laser_timer = 600

		elif self.level == 4:
			self.alien_speed = 3
			self.alien_laser_timer = 500

		self.alien_setup(rows=6, cols=8)
		pygame.time.set_timer(ALIENLASER, self.alien_laser_timer)

	def run(self):
		self.player.update()
		self.alien_lasers.update()
		self.extra.update()
		
		self.aliens.update(self.alien_direction,self.alien_speed)
		self.alien_position_checker()
		self.extra_alien_timer()
		self.collision_checks()
		if not self.aliens and self.level < 4:
			self.level_up()
		
		self.player.sprite.lasers.draw(screen)
		self.player.draw(screen)
		self.blocks.draw(screen)
		self.aliens.draw(screen)
		self.alien_lasers.draw(screen)
		self.extra.draw(screen)
		self.display_lives()
		self.display_score()
		self.victory_message()

class CRT:
	def __init__(self):
		self.tv = pygame.image.load('../graphics/tv.png').convert_alpha()
		self.tv = pygame.transform.scale(self.tv,(screen_width,screen_height))

	def draw(self):
		alpha = randint(75,90)
		self.tv.set_alpha(alpha)
		screen.blit(self.tv,(0,0))
		return alpha

if __name__ == '__main__':
	pygame.init()

	screen_width = 600
	screen_height = 600

	screen = pygame.Surface((screen_width, screen_height))

	display_width, display_height = pygame.display.get_desktop_sizes()[0]

	display = pygame.display.set_mode((display_width, display_height),pygame.NOFRAME)

	overlay = pygame.Surface((display_width, display_height),pygame.SRCALPHA)

	clock = pygame.time.Clock()

	pygame.mouse.set_visible(False)

	game = Game()

	crt = CRT()

	ALIENLASER = pygame.USEREVENT + 1
	pygame.time.set_timer(ALIENLASER,game.alien_laser_timer)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				pygame.quit()
				sys.exit()

			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			if event.type == ALIENLASER and not game.intro and not game.paused and not game.game_over:
				game.alien_shoot()

			if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
				if game.game_over:
					game = Game()

				elif not game.intro:
					game.paused = not game.paused

					if game.paused:
						game.music.stop()
					else:
						game.music.play(loops = -1)

			if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
				if game.intro:
					game.intro = False
					game.music.play(loops = -1)

		screen.fill((30,30,30))

		if game.intro:
			game.intro_screen()
		elif game.game_over:
			game.game_over_menu()
		elif game.paused:
			game.pause_menu()
		else: 
			game.run()

		alpha = crt.draw()

		# Scaling, rendering section
		game_size = min(display_width, display_height)

		scaled_screen = pygame.transform.scale(
			screen,
			(game_size, game_size)
		)

		display.fill((57, 255, 143))

		x = (display_width - game_size) // 2
		y = (display_height - game_size) // 2

		display.blit(scaled_screen, (x, y))

		# CRT lines
		overlay.fill((0, 0, 0, 0))

		line_height = 3
		for scan_y in range(0, display_height, line_height):
			pygame.draw.line(overlay, (0,0,0,alpha), (0,scan_y), (display_width,scan_y), 1)

		display.blit(overlay,(0,0))

		# Display update, frame-rate control
		pygame.display.flip()
		clock.tick(60)