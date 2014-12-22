#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Projekt na AI nr. 2 
# rzeczy ktore sa wspolne dla edytora i dla gierki wlasciwej
# Autorzy: Piotr Czarny i Maciej Danielak

import sys
import os
import math

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
			
		
if __name__ == "__main__":
	sys.exit(0)