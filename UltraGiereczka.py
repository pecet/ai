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
sys.setrecursionlimit(50000)

WIDTH = 1024
HEIGHT = 768
PLAYER_RADIUS=50
levelData = []
levelData = loadLevel()
graph = dict()

def checkIfEdgeInGraph(startNodeX, startNodeY, endNodeX, endNodeY): #zwraca true kiedy dany punk nie laczy sie z drugim punktem
	if ((startNodeX, startNodeY)) in graph:
		if (endNodeX, endNodeY) in graph[(startNodeX, startNodeY)]:
			return False
		else:
			return True
	else:
		return True

#pisalem to wzorujac sie na tym http://pl.wikipedia.org/wiki/Rozrost_ziarna
def floodStart(startX, startY, screen):
	floodFill(startX, startY, startX+PLAYER_RADIUS, startY, screen)
	floodFill(startX, startY, startX, startY+PLAYER_RADIUS, screen)
	floodFill(startX, startY, startX-PLAYER_RADIUS, startY, screen)
	floodFill(startX, startY, startX, startY-PLAYER_RADIUS, screen)

	
def checkIntersection(testline):
	for data in levelData:
		if testline.intersects(data):
			return False
					
def floodFill(startX, startY, endX, endY, screen):#kolizja jeszcze nie dodana
	testLine = Line(Point(startX+1, startY+1), Point(endX, endY)) #musialem tu dodac 1 bo inaczej mialem float division by 0 error. Nie wiem czemu tak sie dzieje. Przez to jest tez ten blad z przechodzeniem czasem siatki przez przeszkody
	if endX>WIDTH or endX<1 or endY>HEIGHT or endY<1 or checkIntersection(testLine)==False:
		pass
	else:
		dodaj = checkIfEdgeInGraph(startX, startY, endX, endY) #przed dodaniem krawedzi do grafu sprawdzamy czy juz jej czasem tam nie ma

		if dodaj == True:
			graph.setdefault((startX, startY), []).append((endX, endY))
			
		if checkIfEdgeInGraph(endX, endY, endX+PLAYER_RADIUS, endY) == True:
			floodFill(endX, endY, endX+PLAYER_RADIUS, endY, screen)#w prawo
		if checkIfEdgeInGraph(endX, endY, endX, endY+PLAYER_RADIUS) == True:
			floodFill(endX, endY, endX, endY+PLAYER_RADIUS, screen)#w gore
		if checkIfEdgeInGraph(endX, endY, endX-PLAYER_RADIUS, endY) == True:
			floodFill(endX, endY, endX-PLAYER_RADIUS, endY, screen)#w lewo
		if checkIfEdgeInGraph(endX, endY, endX, endY-PLAYER_RADIUS) == True:
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
	for key in graph.keys():
		print str(key) + ": " + str(graph[key])
		
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
				
		for key in graph.keys():
			for value in range (0,len(graph[key])):
				pygame.draw.line(screen, (0, 0, 125), (key[0], key[1]), (graph[key][value][0], graph[key][value][1]),2)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:		
				sys.exit(0)		
			elif event.type == pygame.MOUSEMOTION:
				mx, my = pygame.mouse.get_pos()
				#print mx, my

	
	
if __name__ == "__main__":
	main()	