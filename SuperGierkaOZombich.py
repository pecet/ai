#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Projekt na AI nr. 1 
# Autorzy: Piotr Czarny i Maciej Danielak

import pygame
import exceptions
import math
import sys
import copy
import random
import socket
import pickle
import errno
import time
import os
from vec2d import Vec2d

# stale 
WIDTH = 1024
HEIGHT = 768
MOVE_SPEED = 144
ENEMY_SPEED = 99
BULLET_SPEED = 2222
WRAP_AROUND = True # zawijac wspolrzedne? (tj - idziemy w prawo i dochodzimy do lewej krawedzi)
NUM_OBSTACLES = 11
NUM_ENEMIES = 8
DONT_CLEAR = False # true - nie odswiezamy ekranu, przydatne tylko dla jednego/malo enemiesow bo wtedy sie ladne sciezka narysuje
ENEMY_RADIUS = 13
OBSTACLE_MIN_RADIUS = 20
OBSTACLE_MAX_RADIUS = 60

# zmienne
obstacles = []
enemies = []
bullets = []
player = None
clock = pygame.time.Clock()


def circleCollision(x1, y1, r1, x2, y2, r2):
	return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= (r1 + r2) ** 2
	
def rotCenter(image, angle): # pygame nie ma tego standardowo[!] ( http://www.pygame.org/wiki/RotateCenter?parent=CookBook )
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image	
	
def truncate(vector, max):
	if not type(vector) is Vec2d:
		raise Exception("truncate potrzebuje wektora jako 1 parametr")
	if(vector.get_length() > max):
		return vector.normalized() * max # normalized juz zwraca kopie zmiennej
	else:
		return Vec2d(vector) # kopia
		

def matrixMultiply(X, Y): # http://www.programiz.com/python-programming/examples/multiply-matrix
	result = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*Y)] for X_row in X]
	return result
	
# translacja funkcji z cpp na pythona (mam nadzieje ze dobrze)
# zrodla w cpp:
# https://github.com/chenyukang/Basketball_demo/blob/master/src/C2DMatrix.h
# http://read.pudn.com/downloads121/sourcecode/graph/516833/Buckland_Chapter4-SimpleSoccer/Common/2D/Transformations.h__.htm
	
def transformVector(vector, matrix):
	m11 = matrix[0][0]
	m12 = matrix[0][1]
	m13 = matrix[0][2]

	m21 = matrix[1][0]
	m22 = matrix[1][1]
	m23 = matrix[1][2]	
	
	m31 = matrix[2][0]
	m32 = matrix[2][1]
	m33 = matrix[2][2]		
	
	x = (vector.x * m11) + (vector.y * m21) + (m31)
	y = (vector.x * m12) + (vector.y * m22) + (m32)	
	return Vec2d(x, y)
	
def pointToWorldSpace(point, heading, side, position):
	rotate = [[heading.x, heading.y, 0], 
	[side.x, side.y, 0],
	[0, 0, 1]]
	
	translate = [[1, 0, 0],
	[0, 1, 0],
	[position.x, position.y, 1]]
	
	transform = matrixMultiply(rotate, translate)
	return transformVector(point, transform)
	
def vectorToWorldSpace(vec, heading, side):
	rotate = [[heading.x, heading.y, 0], 
	[side.x, side.y, 0],
	[0, 0, 1]]
	
	return transformVector(vec, rotate)	
	
def vectorToLocalSpace(vec, heading, side):
	trans = [[heading.x, side.x, 0], 
	[heading.y, side.y, 0],
	[0, 0, 1]]

	return transformVector(vec, trans)
			
def pointToLocalSpace(point, heading, side, position):

	tx = -position.dot(heading)
	ty = -position.dot(side)

	trans = [[heading.x, side.x, 0], 
	[heading.y, side.y, 0],
	[tx, ty, 1]]

	return transformVector(point, trans)
	
	
		
def changeBehaviorOfAll(enemies, behavior):
	for en in enemies:
		en.changeBehavior(behavior)

# https://code.google.com/p/thinksharp/source/browse/trunk/Steering/GameWorld.cs?r=7
def tagObstaclesWithinViewRange(obstacles, enemy, radius):
	counter = 0
	for ob in obstacles:
		ob.tag = False
		to = ob.position() - enemy.position()
		range = radius + ob.r
		if (ob != enemy) and (to.get_length_sqrd() < range * range):
			ob.tag = True
			counter += 1
			
	return counter # tylko dla testu w sumie
		
class Obstacle:
	def __init__(self):
		self.x = random.randrange(0, WIDTH)
		self.y = random.randrange(0, HEIGHT)
		self.r = random.randrange(OBSTACLE_MIN_RADIUS, OBSTACLE_MAX_RADIUS)
		self.tag = False
	def set(self, x, y, r):
		self.x = x
		self.y = y
		self.r = r
	def draw(self, screen):
		pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), self.r, 0)
	def position(self):
		return Vec2d(self.x, self.y)

class Enemy:
	def __init__(self, obstacles, player):
				
		# to musimy zeby nie trafic czasem w miejsce w ktorym znajduje sie obstacles
		# bo wtedy przeciwnik bylby na starcie w scianie
		# nie mozemy wejsc tez w playerka (trzeba jakis dystans zachowac)
		# aby mu dac szanse na ucieczke
	
		repeatRandom = True
		self.r = ENEMY_RADIUS
		
		while repeatRandom:
			self.x = random.randrange(25, WIDTH - 25)
			self.y = random.randrange(25, HEIGHT - 25)
			
			repeatRandom = False
			for ob in obstacles:
				if circleCollision(ob.x, ob.y, ob.r, self.x, self.y, self.r):
					#print 'kolizja zombiaka z przeszkoda podczas tworzenia - szukamy nowej pozycji'
					repeatRandom = True
					break
			
			# sprawdzamy czy nie jestesmy zbyt blisko gracza (+ 100 odleglosc od gracza)
			if circleCollision(player.x, player.y, player.r + 100, self.x, self.y, self.r):
				repeatRandom = True

		
		self.velocity = Vec2d(0, 0)
		self.heading = Vec2d(0, 0)
		self.side = Vec2d(0, 0)
		self.speed = 0
		self.maxSpeed = ENEMY_SPEED
		self.wanderTarget = Vec2d(WIDTH / 2, HEIGHT / 2)
		self.changeBehavior('hide')
		self.tag = False
		
	def set(self, x, y, r):
		self.x = x
		self.y = y
		self.r = r

	def position(self):
		return Vec2d(self.x, self.y)

	def draw(self, screen):
		pygame.draw.circle(screen, (0, 196, 0), (int(self.x), int(self.y)), self.r, 0)	

	def changeBehavior(self, behavior):
		# self.steering to referencja do wlasciwej funkcji ktora obsluguje co sie ma dziac z enemiesami
		# cos ala function pointery z C tylko w pythonie
	
		if behavior == 'seek': self.steering = self.seek
		elif behavior == 'flee': self.steering = self.flee
		elif behavior == 'arrive': self.steering = self.arrive
		elif behavior == 'pursuit': self.steering = self.pursuit
		elif behavior == 'evade': self.steering = self.evade
		elif behavior == 'wander': self.steering = self.wander
		elif behavior == 'hide': self.steering = self.hide		
		else: raise Exception("changeBehavior: nieznana wartosc parametru behavior")
		self.behavior = behavior
		
	# ------------ steering behaviors 
	def seek(self, player, obstacles, enemies, dt):		
		desiredVelocity = Vec2d(player.position() - self.position()).normalized() * self.maxSpeed		
		return desiredVelocity - self.velocity
			
	def flee(self, player, obstacles, enemies, dt):
		desiredVelocity = Vec2d(self.position() - player.position()).normalized() * self.maxSpeed		
		return desiredVelocity - self.velocity
		
	def arrive(self, player, obstacles, enemies, dt):
		toTarget = player.position() - self.position()
		dist = toTarget.get_length()
		
		if dist > 0:
			speed = dist / 4.5 # <-- de-acceleration tweaker
			#print speed
			speed = min(speed, self.maxSpeed)
			desiredVelocity = toTarget * (speed / dist)
			return desiredVelocity - self.velocity
			
		return Vec2d(0, 0)
		
	def pursuit(self, player, obstacles, enemies, dt):
		toEvader = player.position() - self.position()
		relativeHeading = self.heading.dot(player.heading())
		if (toEvader.dot(self.heading) > 0) and (relativeHeading < -0.95):
			return self.seek(player, obstacles, enemies, dt)
			
		lookAheadTime = toEvader.get_length() / (self.maxSpeed + player.velocity.get_length()) #velocity.get_leght == speed
		
		# seek 
		#seekFor = player.position() + player.heading() * MOVE_SPEED * lookAheadTime
		seekFor = player.position() + player.velocity * lookAheadTime
		desiredVelocity = Vec2d(seekFor - self.position()).normalized() * self.maxSpeed		
		return desiredVelocity - self.velocity
		

	def evade(self, player, obstacles, enemies, dt):	
		toPurser = player.position() - self.position()
		lookAheadTime = toPurser.get_length() / (self.maxSpeed + player.velocity.get_length()) #velocity.get_leght == speed
		
		#flee
		fleeFrom = player.position() + player.velocity * lookAheadTime
		desiredVelocity = Vec2d(self.position() - fleeFrom).normalized() * self.maxSpeed		
		return desiredVelocity - self.velocity

	
	def wander(self, player, obstacles, enemies, dt): 
		# ja tak te parametry rozumiem (+ sprawdzone doswiadczalnie przez ich zmiane)
		wanderRadius = 200 # promien kola po ktorym poruszamy sie (im wiecej tym mniejszy) / jak bardzo skrecamy 0 = linia prosta
		wanderDistance = 40 # odleglosc od srodka kola / podobienstwo do idealnego kola
		wanderJitter = 200 # stopien losowosci (wiecej = bardziej losowo) 0 = idealne kola
		self.wanderTarget += Vec2d(random.uniform(-1.0, 1.0) * wanderJitter, random.uniform(-1.0, 1.0) * wanderJitter)
		self.wanderTarget = self.wanderTarget.normalized()
		self.wanderTarget *= wanderRadius
		
		targetLocal = self.wanderTarget + Vec2d(wanderDistance, 0)
		targetWorld = pointToWorldSpace(targetLocal, self.heading, self.heading.perpendicular(), self.position())
		
		# targetWorld = pointToWorldSpace(targetLocal, player.heading(), player.heading().perpendicular(), player.position()) # uncomment me = tez ciekawy efekt ale chyba nie o to chodzi :)		
		
		toReturn = targetWorld - self.position()
		
		# tego w sumie nie ma w ksiazce ale IMHO musi byc BO gdy velocity = 0 to heading = 0 bo nigdzie sie nie poruszamy a skoro tak to dalej sie nie bedziemy poruszac wiec jakis fallback musi byc czy cos :)		
		if toReturn.get_length() < 0.0001: 
			return self.seek(player, obstacles, enemies, dt)
		
		return toReturn

		
	def getHidingPosition(self, obstacle, posTarget):
		distanceFromBoundary = 35.0
		distanceAway = distanceFromBoundary + obstacle.r
		
		toObstacle = obstacle.position() - posTarget
		toObstacle = toObstacle.normalized()
		return (toObstacle * distanceAway) + obstacle.position()
		
		
	def hide(self, player, obstacles, enemies, dt):
	
		distToClosest = float("inf")
		bestHidingSpot = None
	
		for ob in obstacles:
			hidingSpot = self.getHidingPosition(ob, self.position())
			dist = hidingSpot.get_dist_sqrd(self.position())
			
			if dist < distToClosest:
				distToClosest = dist
				bestHidingSpot = hidingSpot
			
		if distToClosest == float("inf"):
			return self.evade(player, obstacles, enemies, dt)
		else:
			# ------------- arrive ---------------------
			toTarget = bestHidingSpot - self.position()
			dist = toTarget.get_length()
		
			if dist > 0:
				speed = dist / 4.5 # <-- de-acceleration tweaker
				#print speed
				speed = min(speed, self.maxSpeed)
				desiredVelocity = toTarget * (speed / dist)
				return desiredVelocity - self.velocity
	
		
	# ---------------------------------
	def avoidance(self, obstacles):
		steeringForce = Vec2d(0, 0)

		minDetectionBoxLength = 14
		boxLength = minDetectionBoxLength + (self.speed / self.maxSpeed) * minDetectionBoxLength
		#tagObstaclesWithinViewRange(obstacles, self, boxLength)
		distToClosestIP = float("inf")
		closestIntersectingObstacle = None
		localPosOfClosestObstacle = Vec2d(0, 0)
		
		for ob in obstacles:
		
			# optymalizacja: zastepuje tagObstaclesWithinViewRange, po co dwa razy iterowac po calej tablicy przeszkod? bez sensu
			ob.tag = False
			to = ob.position() - self.position()
			range = boxLength + ob.r
			if (ob != self) and (to.get_length_sqrd() < range * range):
				ob.tag = True
		
			if ob.tag:
				localPos = pointToLocalSpace(ob.position(), self.heading, self.side, self.position())
				if localPos.x >= 0:
					expandedRadius = ob.r + self.r
					if math.fabs(localPos.y) < expandedRadius:
						cX = localPos.x
						cY = localPos.y
						sqrtPart = math.sqrt(expandedRadius * expandedRadius - cY * cY)
						ip = cX - sqrtPart
						
						if ip <= 0:
							ip = cX + sqrtPart
							
						if ip < distToClosestIP:
							distToClosestIP = ip
							closestIntersectingObstacle = ob
							localPosOfClosestObstacle = localPos
						
		if closestIntersectingObstacle:
			multiplier = 666.0 + (boxLength - localPosOfClosestObstacle.x) / boxLength
			steeringForce.y = (closestIntersectingObstacle.r - localPosOfClosestObstacle.y) * multiplier
			brakingWeight = 0.46
			steeringForce.x = (closestIntersectingObstacle.r - localPosOfClosestObstacle.x) * brakingWeight
			
			steeringForce = vectorToWorldSpace(steeringForce, self.heading, self.side)
				
		return steeringForce
	
	
	# ---------------------------------
		
	def update(self, player, obstacles, bullets, enemies, dt):
		steeringForce = self.steering(player, obstacles, enemies, dt)
		avoidForce = self.avoidance(obstacles + enemies)
		acceleration = (steeringForce - avoidForce) #/ 1.0 # wspolczynnik masy albo jakikolwiek skalujacy przyspieszenie
		self.velocity += acceleration * dt
		self.velocity = truncate(self.velocity, self.maxSpeed)
		self.heading = self.velocity.normalized()
		self.speed = self.velocity.get_length()
		self.side = self.heading.perpendicular()
		newPosition = Vec2d(self.x, self.y) + (self.velocity * dt)
		self.x = newPosition.x
		self.y = newPosition.y
		
		
		# "zawijanie" wspolrzednych x oraz y
		if WRAP_AROUND:
			if self.x > WIDTH:
				self.x = 0.0
			elif self.x < 0.0:
				self.x = WIDTH
			if self.y > HEIGHT:
				self.y = 0.0
			elif self.y < 0.0:
				self.y = HEIGHT
				
		#print str(player.time_elapsed_since_last_action)
		
		if player.vulnerable == False:
			#print player.time_elapsed_since_last_action
			player.time_elapsed_since_last_action += clock.tick()
			if player.time_elapsed_since_last_action > 2000:
				player.vulnerable = True
				print player.vulnerable
				print player.time_elapsed_since_last_action
				return False
			
		if circleCollision(player.x, player.y, player.r, self.x, self.y, self.r): #kolizja przeciwnika z graczem - dodane tutaj, a nie w graczu bo w graczu nie dzialala w przypadku gdy gracz stal w miejscu
			if player.vulnerable == True:
				player.time_elapsed_since_last_action = 0
				player.vulnerable = False
				player.hp = player.hp - 10 #todo - poprawic hp i stworzyc wyswietlanie na ekranie
				print 'HP = ' + str(player.hp)
				print player.vulnerable

		for bu in bullets: #kolizja z przeciwnikami
			if circleCollision(bu.x, bu.y, bu.r, self.x, self.y, self.r):
				enemies.remove(self)
				break
				
	def __repr__(self):
		return 'position=%s, velocity=%s, heading=%s' % (self.position(), self.velocity, self.heading)

	
class Bullet:

	def __init__(self, player, mousex, mousey):
		self.x = player.x
		self.y = player.y
		self.r = 3
		self.velocity = Vec2d(mousex - player.x  , mousey - player.y)
		self.heading = Vec2d(0, 0)
		self.side = Vec2d(0, 0)
		
		self.speed = BULLET_SPEED
		print self.velocity
		
	def draw(self, screen):
		#print "I'm draw!"
		pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.r, 0) #kolor czerwony i mala predkosc tylko do testow
	
	def position(self):
		return Vec2d(self.x, self.y)
		
	def update(self, player, obstacles, enemies, dt):
		
		self.velocity += dt
		#self.velocity = truncate(self.velocity, self.speed)
		self.heading = self.velocity.normalized()
		self.speed = BULLET_SPEED
		newPosition = Vec2d(self.x, self.y) + (self.heading*self.speed * dt)
		self.x = newPosition.x
		self.y = newPosition.y
		
		for ob in obstacles: #kolizja z przeszkodami (przez przeciwnikow ma chyba przenikac)
			if circleCollision(ob.x, ob.y, ob.r, self.x, self.y, self.r):
				bullets.remove(self)
				print "collision"
				break
				

		
		
		
class Player():
	def __init__(self, obstacles):
	
		# jw. ale tylko dla obstaclesow bo zombiaki na pewno nie beda 
		# kolo playera (zapewnione przez powyzsze tworzenie enemiesow ktore jest POZNIEJ)
		
		repeatRandom = True
		while repeatRandom:
			self.x = float(random.randrange(25, WIDTH - 25))
			self.y = float(random.randrange(25, HEIGHT - 25))
			self.r = 10
			self.rot = 0
			self.velocity = Vec2d(0, 0)
			self.hp = 100
			self.vulnerable = True #czy mozemy otrzymac obrazenia - po otrzymaniu obrazen ustawiane na false; chwilowa niesmiertelnosc
			self.time_elapsed_since_last_action = 0 #odliczanie czasu od otrzymania obrazen
			
			repeatRandom = False
			for ob in obstacles:
				if circleCollision(ob.x, ob.y, ob.r, self.x, self.y, self.r):
					repeatRandom = True
					break
					
	def set(self, x, y, rot):
		self.x = x
		self.y = y
		self.rot = rot
		
	def position(self):
		return Vec2d(self.x, self.y)
		
	def heading(self):
		# heading w sumie mozna na dwa sposoby obliczyc albo kierunek predkosci (#1) albo uzywamy kierunku wskazanego przez myszke
		# mysle ze drugi bedzie ok bo w koncu po cos mamy ten kierunek patrzenia
		#return self.velocity.normalized() # 1 
		return Vec2d(1, 0).rotated(self.rot) # 2
		
	def draw(self, screen):
		
		#bouding circle
		pygame.draw.circle(screen, (255, 235, 235), (int(self.x), int(self.y)), self.r, 0)
		
		#wlasciwy trojkat obrotu
		triangle = pygame.Surface((18, 18))
		triangle.fill((255, 255, 255))
		triangle.set_colorkey((255, 255, 255))
		pygame.draw.polygon(triangle, (0, 191, 255), ((0, 0), (18, 0), (9, 18)))
		pygame.draw.aaline(screen, (255, 150, 150), (player.x, player.y), pygame.mouse.get_pos(), 1)
		
		rtriangle = rotCenter(triangle, self.rot + 90) # + 90 bo rysuje od innego wierzcholka niz powinienem
		screen.blit(rtriangle, (self.x - self.r / 1.6, self.y - self.r / 1.6)) # troche taka reczna koretka pozycji trojkata 
		# bo trzeba by skalowac go jeslibysmy chcieli zeby sie dynamicznie zmienial od r a chyba nie o to chodzi) bo on raczej pokazuje tylko
		# obrot gracza
	
	def shoot(self, x, y):
		bullets.append(Bullet(self, x,y))
		
	def checkCollision(self, obstacles):
		for ob in obstacles:
			if circleCollision(ob.x, ob.y, ob.r, self.x, self.y, self.r):
				return True
				

		return False

def reset(behaviorForAll=None):
	global player, obstacles, enemies, bullets

	#inicjujemy zmienne
	
	# sciany 
	obstacles = []
	for i in xrange(0, NUM_OBSTACLES):
		obstacles.append(Obstacle())
		
	# player
	player = Player(obstacles)
		
	# przeciwnicy
	enemies = []
	for i in xrange(0, NUM_ENEMIES):
		enemies.append(Enemy(obstacles, player))
		
	if behaviorForAll is not None:
		changeBehaviorOfAll(enemies, behaviorForAll)
		
def main():
	global player, obstacles, enemies, bullets

	pygame.init()
	pygame.display.set_caption("SuperGierkaOZombich")
	screen = pygame.display.set_mode((WIDTH,HEIGHT))
	
	# test = Vec2d(1, 7)
	# test2 = Vec2d(2, 2)
	# print test * test2
	# print test.dot(test2)
	
	# wcisniete klawisze?
	left = False
	right = False
	up = False
	down = False
	
	reset()
	
	clock = pygame.time.Clock()
	screen.fill((222,222,222)) 
	
	while True: # glowna petla
		dt = clock.tick(60) / 1000.0 # 60 fps max
		# dt = delta czasu ktora naprawde uplynela, clock tick zwraca milisekundy stad dzielenie przez 1000
		#print dt 
		if not DONT_CLEAR:
			screen.fill((222,222,222)) 
	
		for ob in obstacles:
			ob.draw(screen)
			
		for en in enemies:
			en.update(player, obstacles, bullets, enemies, dt)
			en.draw(screen)
			
		for bu in bullets:
			bu.update(player, obstacles, enemies, dt)
			bu.draw(screen)
		#print enemies[0]
			
		player.draw(screen)
			
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit(0)
				
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_w:
					up = True
				elif event.key == pygame.K_s:
					down = True
				if event.key == pygame.K_a:
					left = True
				elif event.key == pygame.K_d:
					right = True	
					
				if event.key == pygame.K_r:
					screen.fill((222,222,222)) 
					if(len(enemies) > 0):
						reset(enemies[0].behavior) # restujemy pamietajac ustawiony behavior
					else:
						reset()
				elif event.key == pygame.K_1:
					changeBehaviorOfAll(enemies, 'seek')
					pygame.display.set_caption("SuperGierkaOZombich: seek")
				elif event.key == pygame.K_2:
					changeBehaviorOfAll(enemies, 'flee')					
					pygame.display.set_caption("SuperGierkaOZombich: flee")
				elif event.key == pygame.K_3:
					changeBehaviorOfAll(enemies, 'arrive')					
					pygame.display.set_caption("SuperGierkaOZombich: arrive")					
				elif event.key == pygame.K_4:
					changeBehaviorOfAll(enemies, 'pursuit')		
					pygame.display.set_caption("SuperGierkaOZombich: pursuit")
				elif event.key == pygame.K_5:
					changeBehaviorOfAll(enemies, 'evade')		
					pygame.display.set_caption("SuperGierkaOZombich: evade")
				elif event.key == pygame.K_6:
					changeBehaviorOfAll(enemies, 'wander')		
					pygame.display.set_caption("SuperGierkaOZombich: wander")
										
					
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_w:
					up = False
				elif event.key == pygame.K_s:
					down = False
				if event.key == pygame.K_a:
					left = False
				elif event.key == pygame.K_d:
					right = False		
					
			elif event.type == pygame.MOUSEMOTION:
				# https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame
				mx, my = pygame.mouse.get_pos()
				dx = mx - player.x
				dy = my - player.y
				rads = math.atan2(-dy, dx)
				degs = math.degrees(rads) % 360
				#print 'Kat pomiedzy mysza a playerem:' + str(degs)
				player.rot = degs
				
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				print "shoot"
				x, y = pygame.mouse.get_pos()
				player.shoot(x,y)


		# obslugujemy klawisze i proste kolizje
		
		prevX = player.x
		prevY = player.y

		if left:
			player.x -= MOVE_SPEED * dt
		elif right:
			player.x += MOVE_SPEED * dt
		if up:
			player.y -= MOVE_SPEED * dt
		elif down: 
			player.y += MOVE_SPEED * dt
				
		if left or right or up or down:
			if WRAP_AROUND:
				if player.x > WIDTH:
					player.x = 0.0
				elif player.x < 0.0:
					player.x = WIDTH
				if player.y > HEIGHT:
					player.y = 0.0
				elif player.y < 0.0:
					player.y = HEIGHT				
		
			if player.checkCollision(obstacles):
				player.x = prevX
				player.y = prevY
				
		#	if player.checkCollision(enemies):
		#		player.x = prevX
		#		player.y = prevY
		#		return False
		# musimy to miec bo pursuit i evade uzywaja predkosci gracza
		# do seek, arrive, flee niekoniecznie
		player.velocity = Vec2d(player.x - prevX, player.y - prevY)	
		#print player.velocity.get_length()
				
		pygame.time.wait(1) # bardzo odciaza procesor	
	
if __name__ == "__main__":
	main()
