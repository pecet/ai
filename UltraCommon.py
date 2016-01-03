#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Projekt na AI nr. 2 
# rzeczy ktore sa wspolne dla edytora i dla gierki wlasciwej
# Autorzy: Piotr Czarny i Maciej Danielak

import sys
import os
import math
import pygame
import random
import pickle
from vec2d import Vec2d
try:
	import pyximport
	pyximport.install()
	
	import intersections_cy as inter
	from intersections_cy import vec
except ImportError:
	import intersections_py as inter
	from intersections_py import vec

BULLET_SPEED = 1500
#bullets = []
#Bullet.bullets = bullets

class Circle:
	def __init__(self, x, y, radius):
		self.x = x
		self.y = y
		self.radius = radius
	def __repr__(self):
		return "x:" + str(self.x) + " y:" + str(self.y) + " radius:" + str(self.radius)
	def dot(self, v):
		return self.x*v.x + self.y*v.y
	def lensq(self):
		return self.dot(self)	
	def len(self):
		return sqrt(self.lensq())
		
	def circleLineCollision(self, Line):
		testseg = inter.Segment(vec(Line[0].x,Line[0].y), vec(Line[1].x,Line[1].y))
		testcirc = inter.Circle(vec(self.x, self.y), self.radius)
		#print inter.segment_circle(testseg, testcirc).len()
		if (inter.segment_circle(testseg, testcirc).len()>0):
			print 'col!'
			return True
		
		'''
	def circleLineCollision(self, Line):
		baX = float(Line[1].x - Line[0].x)
		baY = float(Line[1].y - Line[0].y)
		caX = float(self.x - Line[0].x)
		caY = float(self.y - Line[0].y)
		
		a = (baX * baX) + (baY * baY)
		bBy2 = (baX * caX) + (baY * caY)
		c = (float(caX * caX)) + (float(caY * caY)) - (float(self.radius * self.radius))
		pby2 = float(bBy2 / a)
		q = c/a
		disc = pby2 * pby2 - (q)
		if (disc < 0):
			return False
		else:
			print Line
			print "collCircle"
			return True
			#if (delta < 0): # No intersection
			return False'''
	'''# Transform to local coordinates
		
		LocalP1X = float(Line[0].x - self.x)
		LocalP1Y = float(Line[0].y - self.y)
		LocalP2X = float(Line[1].x - self.x)
		LocalP2Y = float(Line[1].y - self.y)
		# Precalculate this value. We use it often
		P2MinusP1X = float(LocalP2X - LocalP1X)
		P2MinusP1Y = float(LocalP2Y - LocalP1Y)

		a = float((P2MinusP1X) * (P2MinusP1X)) + float((P2MinusP1Y) * (P2MinusP1Y))
		b = float(2 * ((P2MinusP1X * LocalP1X)) + float((P2MinusP1Y * LocalP1Y)))
		c = (float(LocalP1X * LocalP1X)) + (float(LocalP1Y * LocalP1Y)) - (float(self.radius * self.radius))
		delta = b * b - (4 * a * c)
		if (delta < 0):
			return False
		else:
			print Line
			print "collCircle"
			return True
			#if (delta < 0): # No intersection
			return False'''

class Point:
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
	def __repr__(self):
		return "x:" + str(self.x) + " y:" + str(self.y)

class Line:
	def __init__(self, p0 = Point(), p1 = Point()):
		self.p = []
		self.p.append(p0)
		self.p.append(p1)
	def __repr__(self):
		return "{p[0]=" + str(self.p[0]) + "; p[1]=" + str(self.p[1]) + "}"
	def __getitem__(self, key):
		return (self.p[key])
	def intersects(self, other):
		return self.__line_intersects(self.p[0].x, self.p[0].y, self.p[1].x, self.p[1].y, other.p[0].x, other.p[0].y, other.p[1].x, other.p[1].y)
		
	# adaptacja z https://gist.github.com/Joncom/e8e8d18ebe7fe55c3894
	def __line_intersects(self, p0_x, p0_y, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):
		 		
		s1_x = float(p1_x - p0_x) 
		s1_y = float(p1_y - p0_y) 
		s2_x = float(p3_x - p2_x)
		s2_y = float(p3_y - p2_y)
		
		s = 0
		t = 0		
		mianownik = float(-s2_x * s1_y + s1_x * s2_y)

		if math.fabs(mianownik) == 0:
			return False
		else:
			s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / mianownik;
			t = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / mianownik;

		#print s, t
		 
		if (s >= 0 and s <= 1 and t >= 0 and t <= 1):
			#print p0_x, p0_y, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y
			#print "collLine"
			return True
		 
		return False
		
class FSM:
	def __init__(self, enemy, graph):
		self.enemy = enemy
		self.state = None
		self.graph = graph
		
	def getStateAsString(self):
		return self.state.__class__.__name__
	def update(self):
		#---------- tutaj wywolujemy rzeczy ktore robi wybrany stan -------
		if self.state:
			self.state.execute(self.enemy, self.graph)
	def changeState(self, newState):
		if self.state:
			self.state.exit(self.enemy, self.graph)
			
		self.state = newState
		
		if self.state:
			self.state.enter(self.enemy, self.graph)

class State:
	def enter(self, enemy, graph):
		pass
	def execute(self, enemy, graph):
		pass
	def exit(self, enemy, graph):
		pass
		
class GoToRandomPointState(State):
	def enter(self, enemy, graph):
		if not graph: return 
		rrr = random.choice(graph.keys())
		enemy.goTo(rrr[0], rrr[1]) 
	def execute(self, enemy, graph):
		if enemy.hp < 75:
			enemy.FSM.changeState(GoToApteczka())
			return
	
		if enemy.followPath() == False:
			self.enter(enemy, graph)
		
	def exit(self, enemy, graph):
		pass
	
class GoToApteczka(State):
	def enter(self, enemy, graph):
		if not graph: return 
		if not Pickup.pickups: return
		
		bestPickup = None
		bestodl = 9999999
		for p in Pickup.pickups:
			x1 = enemy.pos.x
			y1 = enemy.pos.y 
			x2 = p.pos.x
			y2 = p.pos.y
			newodl = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) 
			if newodl < bestodl:
				bestodl = newodl
				bestPickup = p
			
		#rrr = random.choice(Pickup.pickups)
		
		rrr = bestPickup
		enemy.goTo(rrr.pos.x, rrr.pos.y) 
	def execute(self, enemy, graph):
		if enemy.hp > 75:
			enemy.FSM.changeState(GoToRandomPointState())
			return	
	
	
		mamyTamJeszczeApteczke = False # sprawdzamy czy apteczka dalej jest tam gdzie idziemy, bo np. inny przeciwnik mogl ja juz zjesc :)
		if enemy.droga:
			ost = enemy.droga[-1] # ostatni element drogi
			for p in Pickup.pickups:
				x = p.pos.x
				y = p.pos.y 
				if ost[0] == x and ost[1] == y:
					mamyTamJeszczeApteczke = True
					break
			
		if enemy.followPath() == False:
			self.enter(enemy, graph)
			return
		
		if mamyTamJeszczeApteczke == False:
			self.enter(enemy, graph)
			return			
		
	def exit(self, enemy, graph):
		pass
		
class ShootEnemy(State):
	def enter(self, enemy, graph):
		if not graph: return 
	def exit(self, enemy, graph):
		pass		
		

class Enemy:
	# statyczne zmienne
	graph = None
	enemies = None

	def __init__(self, pos = Point()):
		self.pos = pos
		self.r = 10
		self.droga = [] 
		self.drogaIndeks = 0
		self.FSM = FSM(self, Enemy.graph)
		self.FSM.changeState(GoToRandomPointState())
		self.hp = 1
		self.color = random.randint(10,255)
		self.color2 = random.randint(10,255)
		self.color3 = random.randint(10,255)
		
	def draw(self, screen):
		pygame.draw.circle(screen, (self.color, self.color2, self.color3), (self.pos.x, self.pos.y), self.r)
		
	def copyDict(self, graph, wartosc = 0):
		ret = dict()
		for key in graph.keys():
			ret[key] = wartosc
			#print key
			
		return ret
		
	def minFromDict(self, gdzieSzukac, skadWartosc):
		naj = 999999
		najx = None
		for x in gdzieSzukac:
			#print str(x) + "->" + str(skadWartosc[x])
			if skadWartosc[x] < naj:
				naj = skadWartosc[x]
				najx = x
		return najx
		
	def HEUR(self, x1, y1, x2, y2): #heurystyka
		#return 0 # ciekawostka jak damy to to mamy algorytm dijkstry (sprawdzi wszystkie wartosci w grafie)
		#return 10 * ( abs(x1 - x2) + abs(y1 - y2) )
		xD = abs(x1 - x2)
		yD = abs(y1 - y2)
		return 0
		if xD > yD:
			return (14 * yD + 10 * (xD - yD)) 
		else:
			return (14 * xD + 10 * (yD - xD)) 
			
	def HEUR2(self, H, x1, y1, x2, y2): # inna heurystyka
		return float(H + abs(x1 * y2 - x2 * y1) * 0.001)
		
	def distBetween(self, x1, y1, x2, y2):
		#hack
		a = x1 - x2
		b = y1 - y2
		if a == 0 or b == 0:
			#print 'skos'
			return 10
		else:
			#print 'nieskos'
			return 14
		
	def aStar(self, koniecX, koniecY):
		graph = Enemy.graph 
		# zeby bylo zapisane w takiej samej formie jak w grafie
		poczatek = (self.pos.x, self.pos.y)
		koniec = (koniecX, koniecY)
		otwarte = []
		zamkniete = []
		F = self.copyDict(graph)
		G = self.copyDict(graph)
		H = self.copyDict(graph)
		rodzic = self.copyDict(graph, None)
		otwarte.append(poczatek)
		#print self.minFromDict(otwarte, F)
		
		licznik = 0 # takie licznik z ciekawosci
		
		while True:
			licznik += 1
			if koniec in zamkniete:
				#print 'Jest droga.'
				#print 'Liczba wywolan petli: ' + str(licznik) + ' ilosc kluczy w grafie: ' + str(len(graph))
				# robimy droge elo
				
				droga = []
				czego = koniec
				while True:
					if czego == None:
						break
					droga.append(czego)
					czego = rodzic[czego]
				
				droga.reverse()
				#print 'Dlugosc drogi:' + str(len(droga))
				
				return droga
			
			if not otwarte:
				#print 'Nie da sie tam dojsc albo algorytm zle dziala :/'
				#print 'Liczba wywolan petli: ' + str(licznik) + ' ilosc kluczy w grafie: ' + str(len(graph))
				return None
			
			#print "Otwarte = " + str(otwarte)
			#print "Zamkniete = " + str(zamkniete)
			
			aktualnePole = self.minFromDict(otwarte, F)
			
			#print "AktualnePole = " + str(aktualnePole)
			
			otwarte.remove(aktualnePole)
			zamkniete.append(aktualnePole)
			
			# to jest niepotrzebne, ale kiedys bylo, zostawmy z nostalgi
			# try:
				# gr = graph[aktualnePole]
			# except KeyError:
				# continue
			
			for sasiad in graph[aktualnePole]:
				#print "   Sasiad = " + str(sasiad)
				if sasiad in zamkniete:
					continue
				
				nowyKosztG = G[aktualnePole] + self.distBetween(aktualnePole[0], aktualnePole[1], sasiad[0], sasiad[1])
				
				if sasiad not in otwarte:
					otwarte.append(sasiad)
					rodzic[sasiad] = aktualnePole
					G[sasiad] = nowyKosztG
					H[sasiad] = self.HEUR(sasiad[0], sasiad[1], koniecX, koniecY)
					F[sasiad] = G[sasiad] + H[sasiad]
				else:
					if nowyKosztG < G[sasiad]: 
						#print 'dat'
						rodzic[sasiad] = aktualnePole
						G[sasiad] = nowyKosztG
						H[sasiad] = self.HEUR(sasiad[0], sasiad[1], koniecX, koniecY)
						F[sasiad] = G[sasiad] + H[sasiad]			
		
	
	def goTo(self, koniecX, koniecY):
		closestToSelf = closestPointInGraph(Enemy.graph, self.pos.x, self.pos.y)
		if not closestToSelf:
			return
		self.pos.x = closestToSelf[0]
		self.pos.y = closestToSelf[1]
	
		droga = self.aStar(koniecX, koniecY)
		if not droga:
			droga = []			
		self.droga = droga
		self.drogaIndeks = 0
		
	def shoot(self, bullets, shooter, enemy):
		bullets.append(Bullet(self, enemy))
		
	def followPath(self): # true jak sie cos przesunelismy, false jak sie nic nie przesunelismy (bo np. koniec drogi)
		if not self.droga:
			return False
		elif self.drogaIndeks >= len(self.droga):
			return False
			
		# prosty path following
		#target x i y
		x = self.droga[self.drogaIndeks][0]
		y = self.droga[self.drogaIndeks][1]
		#print x, y
		if x == self.pos.x and y == self.pos.y:
			self.drogaIndeks += 1
			return True
		if self.pos.x < x:
			self.pos.x += 1
			#return True
		elif self.pos.x > x:
			self.pos.x -= 1
			#return True	
		if self.pos.y < y:
			self.pos.y += 1
			#return True
		elif self.pos.y > y:	
			self.pos.y -= 1
			#return True
		
		return True
	
class Bullet:

	def __init__(self, shooter, enemy):
		self.x = shooter.pos.x
		self.y = shooter.pos.y
		self.r = 5
		self.velocity = Vec2d(enemy.pos.x - shooter.pos.x  , enemy.pos.y - shooter.pos.y)
		self.heading = Vec2d(0, 0)
		self.side = Vec2d(0, 0)
		
		self.speed = BULLET_SPEED
		#print self.velocity
		
	def draw(self, screen):
		#print "I'm drawn!"
		pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.r, 0) #kolor czerwony i mala predkosc tylko do testow
	
	def position(self):
		return Vec2d(self.x, self.y)
		'''
	def circleLineCollision(self, Line):
	# Transform to local coordinates
		#print Line
		LocalP1X = Line[0].x - self.x
		LocalP1Y = Line[0].y - self.y
		LocalP2X = Line[1].x - self.x
		LocalP2Y = Line[1].y - self.y
		# Precalculate this value. We use it often
		P2MinusP1X = LocalP2X - LocalP1X
		P2MinusP1Y = LocalP2Y - LocalP1Y

		a = (P2MinusP1X) * (P2MinusP1X) + (P2MinusP1Y) * (P2MinusP1Y)
		b = 2 * ((P2MinusP1X * LocalP1X) + (P2MinusP1Y * LocalP1Y))
		c = (LocalP1X * LocalP1X) + (LocalP1Y * LocalP1Y) - (self.r * self.r)
		delta = b * b - (4 * a * c)
		if (delta >= 0):
			return True'''
	def bulletLineCollision(self, Line):
		testCircle = Circle(self.x, self.y, self.r)
		if testCircle.circleLineCollision(Line):
			return True
			
	def update(self, enemies, bullets, levelData, dt):#powinien byc tu jeszcze shooter i obstacles?
		self.velocity += dt
		#self.velocity = truncate(self.velocity, self.speed)
		self.heading = self.velocity.normalized()
		self.speed = BULLET_SPEED
		newPosition = Vec2d(self.x, self.y) + (self.heading*self.speed * dt)
		self.x = newPosition.x
		self.y = newPosition.y
		#
		for enemy in Enemy.enemies: #kolizja z przeszkodami (przez przeciwnikow ma chyba przenikac)
			if circleCollision(enemy.pos.x, enemy.pos.y, enemy.r, self.x, self.y, self.r):
				bullets.remove(self)
				print "collision"
				break
				
		for data in levelData:
			#if circleLineCollision((data.p[0].x, data.p[0].y), (data.p[1].x, data.p[1].y), self.x, self.y, self.r):
			if self.bulletLineCollision(data):
				bullets.remove(self)
				print "AAAAAAAAA"
				break

class Pickup:
	#statyczne
	pickups = None

	def __init__(self, type = 0, pos = Point()):
		self.r = 15
		self.pos = pos
		self.type = type # jakby kiedys bylo wiecej, a nie wiem czy bedzie
	def draw(self, screen):
		pygame.draw.circle(screen, (123, 123, 123), (self.pos.x, self.pos.y), self.r)
		pygame.draw.line(screen, (240, 0, 0), (self.pos.x + 9, self.pos.y), (self.pos.x - 9, self.pos.y), 5)
		pygame.draw.line(screen, (240, 0, 0), (self.pos.x, self.pos.y + 9), (self.pos.x, self.pos.y - 9), 5)
	def update(self):
		for enemy in Enemy.enemies:
			if circleCollision(self.pos.x, self.pos.y, self.r, enemy.pos.x, enemy.pos.y, enemy.r):
				enemy.hp += 20
				Pickup.pickups.remove(self)
				return

		
		
	
	
def saveGraph(graph, output="graph_pickle.txt"):
	pickle.dump(graph, open(output, "wb" ))

def loadGraph(input="graph_pickle.txt"):
	return pickle.load(open(input, "rb"))
		
def saveLevel(levelData, output="level.txt"):
	with open(output, "w") as file:
		for data in levelData:
			file.write(str(data.p[0].x) + ", " + str(data.p[0].y) + ", " + str(data.p[1].x) + ", " + str(data.p[1].y) + "\n");
			
def loadLevel(input="level.txt"):
	if not os.path.exists(input):
		return []
		
	levelData = []
	with open(input, "r") as file:
		lines = file.readlines()
	for line in lines:
		s = line.split(",")
		if(len(s) == 4):
			p0x = int(s[0])
			p0y = int(s[1])
			p1x = int(s[2])
			p1y = int(s[3])
			levelData.append(Line(Point(p0x, p0y), Point(p1x, p1y)))
			
	return levelData
			
			
def drawAllEnemies(enemies, screen):
	for enemy in enemies:
		enemy.draw(screen)
		
def updateAllEnemies(enemies):
	for enemy in enemies:
		#enemy.followPath()		
		enemy.FSM.update()
		
def drawAllBullets(bullets, screen):
	for bullet in bullets:
		bullet.draw(screen)
		
#def updateAllBullets(bullets):
	#for enemy in enemies:
	#	enemy.draw(screen)
		
def updateAndDrawPickups(pickups, screen):
	for pickup in pickups:
		pickup.draw(screen)
		pickup.update()
		
def closestPointInGraph(graph, x, y): # najblizszy punkt w grafie do podanego punktu
	odl = 9999999
	co = None
	for key in graph.keys():
		newodl = (key[0] - x) * (key[0] - x) + (key[1] - y) * (key[1] - y) 
		if newodl < odl:
			odl = newodl
			co = key
	
	return co
	
def circleCollision(x1, y1, r1, x2, y2, r2):
	return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= (r1 + r2) ** 2
		
#def circleLineCollision(LineP1, LineP2, CircleCentrex, CircleCentrey, Radius):
	# Transform to local coordinates
#	LocalP1X = LineP1[0] - CircleCentrex
#	LocalP1Y = LineP1[1] - CircleCentrex
#	LocalP2X = LineP2[0] - CircleCentrey
#	LocalP2Y = LineP2[1] - CircleCentrey
	# Precalculate this value. We use it often
#	P2MinusP1X = LocalP2X - LocalP1X
#	P2MinusP1Y = LocalP2Y - LocalP1Y

#	a = (P2MinusP1X) * (P2MinusP1X) + (P2MinusP1Y) * (P2MinusP1Y)
#	b = 2 * ((P2MinusP1X * LocalP1X) + (P2MinusP1Y * LocalP1Y))
#	c = (LocalP1X * LocalP1X) + (LocalP1Y * LocalP1Y) - (Radius * Radius)
#	delta = b * b - (4 * a * c)
#	if (delta >= 0):
#		return True
	#if (delta < 0): # No intersection
	#	return False
	#elif (delta == 0): # One intersection
	#	u = -b / (2 * a)
	#	return False#LineP1 + (u * P2MinusP1)
	#	# Use LineP1 instead of LocalP1 because we want our answer in global
	#	#   space, not the circle's local space
	#elif (delta > 0): # Two intersections
	#	SquareRootDelta = math.sqrt(delta)
	#
	#	u1 = (-b + SquareRootDelta) / (2 * a)
	#	u2 = (-b - SquareRootDelta) / (2 * a)
	#	print "!!!!!!!!!collision!"
	#	return True#{ LineP1 + (u1 * P2MinusP1) ; LineP1 + (u2 * P2MinusP1)}

		
		
		
if __name__ == "__main__":
	sys.exit(0)