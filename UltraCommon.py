#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Projekt na AI nr. 2 
# rzeczy ktore sa wspolne dla edytora i dla gierki wlasciwej
# Autorzy: Piotr Czarny i Maciej Danielak

import sys
import os

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