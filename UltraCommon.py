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
			return True
		 
		return False

		
class FSM:
	def __init__(self, enemy, graph):
		self.enemy = enemy
		self.state = None
		self.graph = graph
	def update(self):
		#---------- tutaj trzeba zmieniac stany ------------
		
		
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
		rrr = random.choice(graph.keys())
		enemy.goTo(rrr[0], rrr[1]) 
	def execute(self, enemy, graph):
		if enemy.followPath() == False:
			self.enter(enemy, graph)
		
	def exit(self, enemy, graph):
		pass
	

class Enemy:
	# statyczne zmienne
	graph = None

	def __init__(self, pos = Point()):
		self.pos = pos
		self.r = 5
		self.droga = [] 
		self.drogaIndeks = 0
		self.FSM = FSM(self, Enemy.graph)
		self.FSM.changeState(GoToRandomPointState())
	def draw(self, screen):
		pygame.draw.circle(screen, (255, 0, 0), (self.pos.x, self.pos.y), self.r)
		
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
		
def closestPointInGraph(graph, x, y): # najblizszy punkt w grafie do podanego punktu
	odl = 9999999
	co = None
	for key in graph.keys():
		newodl = (key[0] - x) * (key[0] - x) + (key[1] - y) * (key[1] - y) 
		if newodl < odl:
			odl = newodl
			co = key
	
	return co
		
		
		
		
if __name__ == "__main__":
	sys.exit(0)