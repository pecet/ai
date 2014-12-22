#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Projekt na AI nr. 2 - prosty edytor plansz,
# tylko z dodawaniem rzeczy bez usuwania, i innych ficzerow
# bo po co nam cos bardziej skomplikowanego?
# ale i tak latwiej niz recznie wklepywac te rzeczy
# zapisuje rzaczy jako odcinki, bo chyba tak mialo byc
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
import copy
from UltraCommon import *

WIDTH = 1024
HEIGHT = 768

def main():

	pygame.init()
	pygame.display.set_caption("UltraEdytor")
	screen = pygame.display.set_mode((WIDTH,HEIGHT))
	
	clickPos = None
	
	levelData = []
	levelData = loadLevel()
	finishMe = len(levelData)

	
	while True:
		pygame.time.wait(1) # bardzo odciaza procesor	
		pygame.display.flip()
		screen.fill((222,222,222)) 
		
		if clickPos:
			pygame.draw.circle(screen, (255, 0, 0), (clickPos.x, clickPos.y), 3, 0)
		
		for data in levelData:
			pygame.draw.line(screen, (0, 0, 0), (data.p[0].x, data.p[0].y), (data.p[1].x, data.p[1].y),2)

		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:		
				saveLevel(levelData)
				sys.exit(0)		
			elif event.type == pygame.MOUSEBUTTONDOWN:
				print levelData
				if clickPos == None:
					if event.button == 1:
						x, y = pygame.mouse.get_pos()
						clickPos = Point(x, y)
				else: 
					if event.button == 1:
						x, y = pygame.mouse.get_pos()						
						levelData.append(Line(clickPos, Point(x, y)))
						clickPos = Point(x, y)
					elif event.button == 3:
						if finishMe < len(levelData):
							f = levelData[finishMe]
							levelData.append(Line(clickPos, Point(f.p[0].x, f.p[0].y)))
							finishMe = len(levelData)
							clickPos = None
	
	
if __name__ == "__main__":
	main()	