from functools import partial

import math
import pygame
import time
pygame.init()
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
screenX = 720
screenY = 1350
def collide_rect(a,b):
	if a.top<b.top and a.top+a.height>b.top:
		if a.left<b.left and a.left+a.width>b.left:
			#a.left-=1
			#a.top-=1
			return True
		elif b.left<a.left and b.left+b.width>a.left:
			#a.left+=1
			#a.top-=1
			return True
	elif a.bottom>b.bottom and a.bottom-a.height<b.bottom:
		if a.left<b.left and a.left+a.width>b.left:
			#a.bottom+=1
			#a.left-=1
			return True
		elif b.left<a.left and b.left+b.width>a.left:
			#a.bottom+=1
			#a.left+=1
			return True
def resize_rect(rectangle,FACTOR):
    if FACTOR<=0:return rectangle
    rect=rectangle.copy()
    rect.width/=FACTOR
    rect.height/=FACTOR
    rect.left/=FACTOR
    rect.top/=FACTOR
    return rect
def distance(p,q):
	return math.sqrt((p[0]-q[0])**2+(p[1]-q[1])**2)

class Environment:

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)

    def show(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)

    def showrect(self, screen, ox, oy):
        pygame.draw.rect(screen, GREEN, self.rect.move(ox, oy))

    def show_min_rect(self, screen, ox, oy, px, py):
        factor = 10
        rect = self.rect.copy()
        rect.width /= factor
        rect.height /= factor
        rect.left /= factor
        rect.top /= factor
        rect.left += px
        rect.top += py
        pygame.draw.rect(screen, GREEN, rect.move(ox, oy))

class Envx(Environment):
    def __init__(self, x, y, length):
        super().__init__(x, y, length, 20)
class Envy(Environment):
    def __init__(self, x, y, height):
        super().__init__(x, y, 20, height)

#TOOLS
class Scale:

    def __init__(self, pos, max_level,min = 0):
        self.min = min
        self.max = max_level
        self.pos = pos
        self.level = min
        self.factor = 1
        self.font = pygame.font.Font(pygame.font.get_default_font(), 20)
        self.rectangle = pygame.Rect(*self.pos, self.max + 15 - self.min, 40)

    def write(self, screen, pos, text, color):
        text = str(text)
        screen.blit(self.font.render(text, True, color), pos)

    def show(self, screen):
        length = 100
        width = 40
        pygame.draw.rect(screen, (0, 0, 0), (*self.pos, length, width), 3)
        pygame.draw.line(screen, (200, 0, 0), (self.pos[0] + 5, self.pos[1] + width // 2),
                         [self.pos[0] + length - 5, self.pos[1] + width // 2])
        pygame.draw.circle(screen, (255, 0, 0), (self.pos[0] + 5 + length//self.max*self.level, self.pos[1] + width // 2), 7)
        self.write(screen, (self.pos[0] - 15 - 10 * len(str(self.level)), self.pos[1] + 5), self.level, (0, 0, 0))

        if pygame.mouse.get_pressed()[0] == 1 and self.rectangle.collidepoint(*pygame.mouse.get_pos()):
            self.level = (pygame.mouse.get_pos()[0] - self.pos[0])*self.max//length
            if self.level < self.min:
                self.level = self.min
            elif self.level > self.max:
                self.level = self.max

class Bar:
	def __init__(self,init_pos,length,color,name='',min=0,max=100,orient="horizontal"):
		self.pos=init_pos
		self.length=length
		self.color=color
		self.name=name
		self.max=max
		self.orient=orient
		self.width=5
		self.rect=pygame.Rect(*init_pos,self.length,10)
		self.reverse=None
		self.value=max
		if orient.startswith("v"):
			self.rect.width,self.rect.height=self.rect.height,self.rect.width
	
	def show(self,screen,ox,oy):
		pygame.draw.rect(screen,(0,0,0),(*self.rect.move(ox,oy).topleft,self.width,self.length),self.width//2)
		pygame.draw.rect(screen,self.color,self.rect.move(ox,oy))
	
	def dec(self,value):
		if value<0:
			self.inc(abs(value))
			return
		if self.orient.startswith("h"):
			self.rect.width-=value
			if self.rect.width<0:
				self.rect.width=0
		else:
			self.rect.height-=value
			if self.rect.height<0:
				self.rect.height=0
		self.value-=value
	
	def inc(self,value):
		if self.orient.startswith("h"):
			self.rect.width+=value
			if self.rect.width>self.max:
				self.rect.width=self.max
		else:
			self.rect.height+=value
			if self.rect.height>self.max:
				self.rect.height=self.max
		self.value+=value
class Button:
	def __init__(self,pos,image=None,shape="circle",text=''):
		self.pos=pos
		self.image=pygame.Surface((200,200),pygame.SRCALPHA)
		self.image.fill((0,0,200,150))
		if image:
			self.image=pygame.image.load(image)
		self.shape=shape
		self.color=(0,0,200)
		self.size=200	#or radius
		self.text=text
		self.font=pygame.font.Font(pygame.font.get_default_font(),30)

	def show(self, screen):
		if self.shape == "circle":
			#pygame.draw.circle(screen,(0,00,0),self.pos,self.size,2)
			pygame.draw.circle(screen,self.color,self.pos,self.size)
			screen.blit(pygame.transform.rotate(self.font.render(self.text,1,(0,0,0)),-90),(self.pos[0],self.pos[1]-self.size))
			#screen.blit(self.image,self.pos)
		else:
			pygame.draw.rect(screen,BLACK,(*self.pos,self.size,self.size))
	
	def clicked(self,x,y):
		return distance((x,y),self.pos)<self.size


#GAME
class Player:

    def __init__(self, pos):
        self.pos = list(pos)
        self.rect = pygame.Rect(*pos, 20, 20)
        self.st = time.time()
        self.angle = 0
        self.gun = Gun(5, 0.05, max=50)
        self.bomb_thrown = False
        self.health = 100
        self.lives = 3
        self.deaths = 0
        self.speed = 3
        self.image_key = None
        self.lost = False

    def __str__(self):
        return f"{self.angle}"

    def show(self, screen):
        return
        pygame.draw.rect(screen, BLACK, self.rect)

    # pygame.

    def showrect(self, screen, image, ox, oy):
        rotatedImage = pygame.transform.rotate(image, self.angle)
        screen.blit(rotatedImage, self.rect.move(ox, oy).topleft)

    def hit(self, damage):
        self.health -= damage

    def show_min_rect(self, screen, ox, oy, px, py):
        factor = 10
        rect = self.rect.copy()
        rect.width /= factor
        rect.height /= factor
        rect.left /= factor
        rect.top /= factor
        rect.left += px
        rect.top += py
        pygame.draw.rect(screen, (0, 0, 200), rect)

    # screen.blit(self.rotatedImage,rect.move(ox,oy).topleft)

    def updateMove(self, dx, dy):
        self.rect.left += dx*self.speed
        self.rect.top += dy*self.speed
        self.pos = list(self.rect.topleft)

    def fire(self,name):
        if time.time() - self.st > 0.2 and self.gun.available_bullets:
            return self.gun.fire(self.rect.center, self.angle, name)

    def reset(self, died=True):
        # return	#uncomment in developer mode
        print("You got knocked out")
        self.pos = [100, 50]
        self.rect.topleft = self.pos
        if died:
            self.lives -= 1
            self.deaths += 1
        self.health = 100
        self.gun.available_bullets = self.gun.max_bullets

class Health:
	def __init__(self,pos):
		self.image=pygame.image.load("health.png")
		self.pos=pos
		self.rect=self.image.get_rect()
		self.rect.center=self.pos
		self.value=random.randint(10,100)
		self.st=time.time()
	
	def showrect(self, screen,ox,oy):
		screen.blit(self.image,self.rect.move(ox,oy).topleft)
	
	def show_min_rect(self,screen,ox,oy,px,py):
		rect=self.rect.copy()
		rect.width/=factor
		rect.height/=factor
		rect.left/=factor
		rect.top/=factor
		rect.left+=px
		rect.top+=py
		screen.blit(self.image,rect.move(ox,oy).topleft)


class Bomb:

    def __init__(self, pos, angle, name):
        self.pos = list(pos)
        self.angle = math.radians(angle)
        self.thrownBy = name
        self.radius = 5
        self.bombDistance = 800
        self.st = time.time()
        self.max_living_time = 4  #secs
        self.blastlength = self.bombDistance // 2
        self.to_reach = [self.pos[0] - self.bombDistance * math.sin(self.angle),
                         self.pos[1] - self.bombDistance * math.cos(self.angle)]
        self.blast = False
        self.diffx = self.to_reach[0] - self.pos[0]
        self.diffy = self.to_reach[1] - self.pos[1]
        self.blastTime = 0.5
        self.rect = pygame.Rect(*self.pos, 10, 10)

    def show(self, screen):
        pygame.draw.circle(screen, (0, 0, 200), self.rect.topleft, self.radius)

    def showrect(self, screen, ox, oy):
        pygame.draw.circle(screen, (0, 0, 200), self.rect.move(ox, oy).topleft, self.radius)

    def show_min_rect(self, screen, ox, oy, px, py):
        factor = 10
        rect = self.rect.copy()
        rect.width /= factor
        rect.height /= factor
        rect.left /= factor
        rect.top /= factor
        rect.left += px
        rect.top += py
        pygame.draw.circle(screen, (0, 0, 200), rect.move(ox, oy).topleft, self.radius / factor)

    def fire(self):
        self.diffx = self.to_reach[0] - self.pos[0]
        self.diffy = self.to_reach[1] - self.pos[1]
        self.pos[0] += self.diffx / 100
        self.pos[1] += self.diffy / 100
        self.rect.topleft = self.pos

class BombRect:
    def __init__(self,rect):
        self.rect = pygame.Rect(*rect.topleft,rect.width*30,rect.width*30)
        self.rect.center = rect.topleft
        # self.rect.width*=30
        # self.rect.height*=30
        self.st = time.time()
        self.max_living_time = 0.5  #secs

class Bullet:
    def __init__(self, pos, angle, damage, pehchan=''):
        super().__init__()
        self.pehchan = pehchan
        self.pos = pos
        self.speed = 5
        self.angle = math.radians(angle)
        assert type(damage) == type(5), "Damage should be integer"
        self.damage = damage
        self.rect = pygame.Rect(*pos, 5, 5)

    def fire(self):
        x, y = self.pos
        x -= self.speed * math.sin(self.angle)
        y -= self.speed * math.cos(self.angle)
        self.rect.topleft = (x, y)
        self.pos = [x, y]

    # self.show(screen)

    def show(self, screen, image):
        rotatedImage = pygame.transform.rotate(image, math.degrees(self.angle))
        screen.blit(rotatedImage, self.rect.topleft)

    def show_min_rect(self, screen, ox, oy, px, py):
        return
        rect = self.rect.copy()
        rect.width /= factor
        rect.height /= factor
        rect.left /= factor
        rect.top /= factor
        rect.left += px
        rect.top += py
        pygame.draw.rect(screen, GREEN, rect.move(ox, oy))

class Gun:
    def __init__(self, damage, _time, max=30, rd=1, name=''):
        self.damage = damage
        self.fire_time = _time
        self.max_bullets = max
        self.available_bullets = self.max_bullets
        self.st = time.time()
        self.reload_time = rd
        self.reload_st = None
        self.name = name

    def fire(self, pos, angle, pehchan):
        if time.time() - self.st > self.fire_time:
            self.st = time.time()
            #self.available_bullets -= 1
            if self.available_bullets <= 0:
                if not self.reload_st:
                    self.reload_st = time.time()
                self.reload()
                return
            return Bullet(pos, angle, self.damage, pehchan)
        return None

    def reload(self, enemy=True):

        if time.time() - self.reload_st > self.reload_time:
            self.available_bullets = self.max_bullets
            self.reload_st = None
class Joystick:
	
	def __init__(self,pos,size=30):
		self.pos=pos
		self.joypos=pos
		self.size=size
		self.dist=self.size*4
		self.temp_dist=0
		
	def draw(self,screen):
		RED=(255,0,0)
		BLACK=(0,0,0)
		pygame.draw.circle(screen,RED,self.joypos,self.size)
		pygame.draw.circle(screen,BLACK,self.pos,self.size*4,10)
		#print("show",self.joypos)
		
	def getPos(self,x,y):
		''' returns tuple of (distance,direction)
		angle in degrees '''
		l=pygame.mouse.get_pressed()[0]
		a=b=theta=0
		if l==1:
			x-=self.pos[0]
			y-=self.pos[1]
			if x==0:
				x=0.000000001
			self.temp_dist=distance(self.pos,(x+self.pos[0],y+self.pos[1]))
			if self.temp_dist>self.dist:
				self.temp_dist=self.dist
			theta=math.atan(y/x)
			if x<0:
				theta+=math.radians(180)
			a=self.pos[0]+self.temp_dist*math.cos(theta)
			b=self.pos[1]+self.temp_dist*math.sin(theta)
			self.joypos=(a,b)
			#print("func",a,b)
		else:
			self.joypos=self.pos
		return (self.temp_dist//10,math.degrees(theta))
	
	def reset(self):
		self.joypos=self.pos
	
	def clicked(self,x,y):
		return distance((x,y),self.pos)<self.dist


def create_gun(a, b, c, d, name):
    return Gun(a, b, c, d, name)


gun = {
    # gun parameters - damage, fire time, total bullets, reload time, name to show
    "m249": partial(create_gun, 10, 0.05, 100, 5, 'm249'),
    "m416": partial(create_gun, 15, 0.1, 30, 1, "m416"),
    "shotgun": partial(create_gun, 100, 1, 2, 2, "shotgun"),
    "m762": partial(create_gun, 20, 0.1, 40, 1, "m762"),
    "slr": partial(create_gun, 30, 0.5, 10, 2, "slr"),
    "2m249": partial(create_gun, 10, 0.001, 500, 20, "2m249"),
    "hand": partial(create_gun, 0, 0, 0, 0, "hand")

}
