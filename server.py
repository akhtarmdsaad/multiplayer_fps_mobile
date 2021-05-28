NAME = "Saad"


TEAM = None





import pickle


from _thread import *


from socket import *





from pygame.locals import *





from classes import *


from network_details import *





s = socket(AF_INET, SOCK_STREAM)


s.bind((ip, port))








def _print(*args):


	print("Server:", *args)








print("Listening...")


s.listen(5)


positions = [


	(77, 107),


	(1364, 50),


	(1343, 2744),


	(89, 2726)


	]


players = []


players_images = {


	0: "1.png",


	1: "2.png",


	2: "3.png",


	3: "4.png",


	4: "5.png"


}





players_loaded_images = {}


for key in players_images.keys():

	if key==0:
		players_loaded_images[key] = pygame.transform.rotate(pygame.image.load(players_images[key]),
		-90)


	players_loaded_images[key] = pygame.image.load(players_images[key])





currentPlayer = 0








def handle_client(c, player):


	c.sendall(pickle.dumps(environments))


	c.sendall(pickle.dumps(players_images))


	while True:


		data = pickle.loads(c.recv(16384))


		if not data:


			players.pop(player)


			break


		players[player], _bullet, _bomb = data


		if _bullet:


			bullets.append(Bullet(*_bullet))


		if _bomb:


			bombs.append(Bomb(*_bomb))


		c.sendall(pickle.dumps([


			players,


			[(b.rect, b.angle) for b in bullets],


			[(b.rect, b.radius) for b in bombs],


			[b.rect for b in bomb_rect]


		]))


	c.close()








def connection():


	global currentPlayer


	while True:


		c, a = s.accept()


		currentPlayer = len(players)


		if currentPlayer >= len(positions):


			print("Too Many Players")


			c.close()


		player = Player(positions[currentPlayer])


		player.image_key = currentPlayer


		c.send(pickle.dumps(player))


		players.append(player)


		start_new_thread(handle_client, (c, currentPlayer))


		currentPlayer += 1


	s.close()








# Myself as a player


me = Player(positions[currentPlayer])


me.image_key = currentPlayer


me.rect = players_loaded_images[me.image_key].get_rect()


me.rect.topleft = me.pos


me.gun = gun["m249"]()


players.append(me)


currentPlayer += 1


start_new_thread(connection, ())





# ------------------Main Game Loop--------------------#





screen = pygame.display.set_mode((screenX, screenY))


pygame.display.set_caption(NAME)





# Environment


# Environment


environments = [


	Envx(0, 0, 1400),


	Envx(0, 2800, 1400),


	Envy(0, 0, 2800),


	Envy(1400, 0, 2800 + 40),


	Envy(700, 0, 600),


	Envx(0, 200, 500),


	Envx(500, 700, 700),


	Envy(500, 700, 500),


	Envy(800, 1100, 600),


	Envx(800, 1700, 400),


	Envx(1100, 1200, 1400 - 1100),


	Envx(350, 1400, 800 - 350),


	Envy(500, 1800, 2200 - 1800),


	Envx(0, 2200, 900),


	Envx(1100, 2200, 1400 - 1100),


	Envy(700, 2400, 400)


]





all_rects = []





# bullets


bullets = []


bullet_image = pygame.image.load("bullet.png")





# bombs


bombs = []


bomb_rect = []


shakeright=True




movex = movey = 0





camera = pygame.Rect(*me.pos, screenX, screenY)


cx, cy = camera.center


cam_speed = 80


rmain = pygame.Rect(0, 0, screenX, screenY)


zoom_scaler = Scale((200, 20), 100, 20)


ZOOMFACTOR = zoom_scaler.level


scrolling = False




#joystick and buttons

j1=Joystick((150,150))

j2=Joystick((150,screenY-150),25)

fingerJoy1=fingerJoy2=None

bomb_btn=Button((600,400),text="bomb")

bomb_btn.size=100

scroll_but=Button((screenX-100,600),text="Scroll")

scroll_but.size=40

show_joystick=False







while True:


	try:


		screen.fill((255, 255, 255))


		ZOOMFACTOR = zoom_scaler.level / 10


		zoom_scaler.show(screen)





		# Drawing stuffs


		

		if show_joystick:

			j1.draw(screen)

			j2.draw(screen)

		bomb_btn.show(screen)

		scroll_but.show(screen)

		

		ox = -camera.centerx + (screenX / 2) * ZOOMFACTOR


		oy = -camera.centery + (screenY / 2) * ZOOMFACTOR





		for env in environments:


			pygame.draw.rect(screen, GREEN, resize_rect(env.rect.move(ox, oy), ZOOMFACTOR))


		for p in players:


			rotatedImage=pygame.transform.rotate(


				pygame.transform.scale(players_loaded_images[p.image_key],
				(int(64 / ZOOMFACTOR), int(64 / ZOOMFACTOR))),
				p.angle)

			#rotatedImage.fill((255,255,255,0))


			screen.blit(rotatedImage, resize_rect(p.rect.move(ox, oy), ZOOMFACTOR).topleft)


		for b in bullets:


			b.fire()  # Only Server


			rotatedImage = pygame.transform.rotate(


				pygame.transform.scale(bullet_image, (int(16 / ZOOMFACTOR), int(16 / ZOOMFACTOR))),


				math.degrees(b.angle))


			screen.blit(rotatedImage, resize_rect(b.rect.move(ox, oy), ZOOMFACTOR).topleft)


		for b in bombs:


			b.fire()  # Only Server


			pygame.draw.circle(screen, (0, 0, 200), resize_rect(b.rect.move(ox, oy), ZOOMFACTOR).topleft,


							   math.ceil(b.radius / ZOOMFACTOR))


		for b in bomb_rect:


			pygame.draw.rect(screen, (200, 200, 0), resize_rect(b.rect.move(ox, oy), ZOOMFACTOR))


			


		if not scrolling:


			if camera.centerx < me.rect.centerx:


				camera.centerx += (me.rect.centerx - camera.centerx) / 1000 * cam_speed


			elif camera.centerx > me.rect.centerx:


				camera.centerx -= -(me.rect.centerx - camera.centerx) / 1000 * cam_speed


			if camera.centery < me.rect.centery:


				camera.centery += (me.rect.centery - camera.centery) / 1000 * cam_speed


			elif camera.centery > me.rect.centery:


				camera.centery -= -(me.rect.centery - camera.centery) / 1000 * cam_speed





		for event in pygame.event.get():


			if event.type == QUIT:


				pygame.quit()


			if event.type == KEYDOWN:


				if event.key == K_UP:


					movey = -1


				elif event.key == K_DOWN:


					movey = 1


				if event.key == K_RIGHT:


					movex = 1


				elif event.key == K_LEFT:


					movex = -1


				if event.key == K_SPACE:


					bullets.append(me.fire(TEAM if TEAM else NAME))


				if event.key == K_KP0:


					bombs.append(Bomb(me.rect.center, me.angle, NAME))


				if event.key == K_KP_MINUS:


					ZOOMFACTOR += 0.5


				if event.key == K_KP_PLUS:


					ZOOMFACTOR -= 0.5





			if event.type == KEYUP:


				if event.key == K_UP:


					movey = 0


				elif event.key == K_DOWN:


					movey = 0


				if event.key == K_RIGHT:


					movex = 0


				elif event.key == K_LEFT:


					movex = 0





			if event.type == FINGERDOWN:

				x,y=event.x*screenX,event.y*screenY

				#print(x,y)

				show_joystick=True

				if y<365 and x<500:

					j1.pos=(x,y)

				if y>910 and x<500:

					j2.pos=(x,y)

				if j1.clicked(x,y):

					if not fingerJoy1:	#if finger Joy 1 is None

						fingerJoy1=event

				elif j2.clicked(x,y):

					if not fingerJoy2:

						fingerJoy2=event

			if event.type==FINGERMOTION:

				x,y=event.x*screenX,event.y*screenY

				if scrolling:

					camera.centerx-=event.dx*screenX

					camera.centery-=event.dy*screenY

					continue

				if fingerJoy2 and fingerJoy2.finger_id==event.finger_id:

					fire_speed,fire_angle=j2.getPos((event.x)*screenX,(event.y)*screenY)

					me.angle=270-fire_angle

				if fingerJoy1 and fingerJoy1.finger_id==event.finger_id:

					move_speed,move_angle=j1.getPos((event.x)*screenX,(event.y)*screenY)

					move_speed/=5
					
					movex=move_speed*math.cos(math.radians(move_angle))

					movey=move_speed*math.sin(math.radians(move_angle))
			if event.type==FINGERUP:
				x,y=event.x*screenX,event.y*screenY
				#print("Fingerup",event)
				show_joystick=True
				
				if fingerJoy1:
					if fingerJoy1.finger_id==event.finger_id:
						fingerJoy1=None
						movex=movey=0
				if fingerJoy2:
					if fingerJoy2.finger_id==event.finger_id:
						fingerJoy2=None
			
			if event.type==MOUSEBUTTONDOWN:

				bullets.append(me.fire(TEAM if TEAM else NAME))


			if event.type == MOUSEMOTION:


				rect = resize_rect(me.rect.move(ox, oy), ZOOMFACTOR)


				x = event.pos[0] - rect.centerx


				y = event.pos[1] - rect.centery





				if y == 0:


					y = 0.000001


				if x == 0:


					x = 0.000001





				#me.angle = -math.degrees(math.atan(y / x)) + 90


				#if x > 0:


					#me.angle += 180
		if not fingerJoy1:
			move_speed=move_angle=0
			j1.reset()
		if not fingerJoy2:
			fire_speed=0
			j2.reset()
		if fire_speed>=60//10:
			_bullet=p.fire(fire_angle)
			if isinstance(_bullet,Bullet):
				bullets.append(_bullet)



		# collision for bomb rect and player


		for b in bomb_rect:


			if time.time() - b.st > b.max_living_time:


				bomb_rect.remove(b)


				break


			for p in players:


				if b.rect.colliderect(p.rect):


					p.lost = True


		# collision for bomb and env


		for b in bombs:


			for env in environments:


				if env.rect.collidepoint(*b.rect.center):


					bomb_rect.append(BombRect(b.rect))


					bombs.remove(b)


					break





			if time.time() - b.st > b.max_living_time:


				bomb_rect.append(BombRect(b.rect))


				bombs.remove(b)


				break


		# collision for bullet and env


		for b in bullets:


			for env in environments:


				if env.rect.collidepoint(*b.rect.center):


					bullets.remove(b)


					break


		# collision for player and env


		if movex or movey:


			temp_movex, temp_movey = movex, movey


			for env in environments:


				if env.rect.collidepoint(me.rect.centerx, me.rect.top):


					if temp_movey < 0:


						temp_movey = 0


				elif env.rect.collidepoint(me.rect.centerx, me.rect.bottom):


					if temp_movey > 0:


						temp_movey = 0


				elif env.rect.collidepoint(me.rect.left, me.rect.centery):


					if temp_movex < 0:


						temp_movex = 0


				elif env.rect.collidepoint(me.rect.right, me.rect.centery):


					if temp_movex > 0:


						temp_movex = 0





			me.updateMove(temp_movex, temp_movey)





		pygame.display.update()


	except Exception as e:


		print(e)
		raise

