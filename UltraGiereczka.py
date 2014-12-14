#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Projekt na AI nr. 2 
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
PLAYER_RADIUS=50
levelData = []
levelData = loadLevel()
addedPoints = [] #sprawdzamy ktore punkty juz dodalismy do grafu i ktorych nie musimy drugi raz przelatywac

#pisalem to wzorujac sie na tym http://pl.wikipedia.org/wiki/Rozrost_ziarna
def floodStart(startX, startY, screen):
	floodFill(startX, startY, startX+PLAYER_RADIUS, startY, screen)
	floodFill(startX, startY, startX, startY+PLAYER_RADIUS, screen)
	floodFill(startX, startY, startX-PLAYER_RADIUS, startY, screen)
	floodFill(startX, startY, startX, startY-PLAYER_RADIUS, screen)

def floodFill(startX, startY, endX, endY, screen):#kolizja jeszcze nie dodana
	if ([endX, endY]) in addedPoints or endX>WIDTH or endX<1 or endY>HEIGHT or endY<1:
		print ("koniec")
		pass
	else:
		#print addedPoints
		addedPoints.append([startX, startY])
		addedPoints.append([endX, endY])
		floodFill(endX, endY, endX+PLAYER_RADIUS, endY, screen)#w prawo
		floodFill(endX, endY, endX, endY+PLAYER_RADIUS, screen)#w gore
		floodFill(endX, endY, endX-PLAYER_RADIUS, endY, screen)#w lewo
		floodFill(endX, endY, endX, endY-PLAYER_RADIUS, screen)#w dol
	
	
def main():

	pygame.init()
	pygame.display.set_caption("UltraGiereczka")
	screen = pygame.display.set_mode((WIDTH,HEIGHT))
	
	clickPos = None
	



	mx = 0
	my = 0
	iii = False
	pointsToDraw = []
	floodStart(10,10, screen)

	for data in addedPoints: #to jest tylko po to zeby zobaczyc output - zazwyczaj zapisuje do pliku przy pomocy python UltraGiereczka.py > output.txt z konsoli
		pointsToDraw.extend(data)
		if len(pointsToDraw) == 4:
			print pointsToDraw
			pointsToDraw = []
			
	while True:
		pygame.time.wait(1) # bardzo odciaza procesor	
		pygame.display.flip()
		screen.fill((222,222,222)) 

		testLine = Line(Point(mx, my), Point(mx + 55, my + 55))
			
		pygame.draw.line(screen, (0, 127, 0) if iii else (255, 0, 0), (testLine.p[0].x, testLine.p[0].y), (testLine.p[1].x, testLine.p[1].y),2)
		
		iii = False

				
		for data in levelData:
			pygame.draw.line(screen, (0, 0, 0), (data.p[0].x, data.p[0].y), (data.p[1].x, data.p[1].y),2)
			single = testLine.intersects(data)
			#print single
			if single:  # wystarczy przeciecie z jedna linia
				iii = True
				
		for data in addedPoints:
			pointsToDraw.extend(data)
			
			if len(pointsToDraw) == 4:
				pygame.draw.line(screen, (0, 0, 125), (pointsToDraw[0], pointsToDraw[1]), (pointsToDraw[2], pointsToDraw[3]),2)
				pygame.draw.circle(screen, (0, 0, 255), (pointsToDraw[2], pointsToDraw[3]),5)
				pointsToDraw = []
			
		for event in pygame.event.get():
			if event.type == pygame.QUIT:		
				sys.exit(0)		
			elif event.type == pygame.MOUSEMOTION:
				mx, my = pygame.mouse.get_pos()
				#print mx, my

	
	
if __name__ == "__main__":
	main()	