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

def main():

	pygame.init()
	pygame.display.set_caption("UltraGiereczka")
	screen = pygame.display.set_mode((WIDTH,HEIGHT))
	
	clickPos = None
	
	levelData = []
	levelData = loadLevel()

	
	while True:
		pygame.time.wait(1) # bardzo odciaza procesor	
		pygame.display.flip()
		screen.fill((222,222,222)) 

		for data in levelData:
			pygame.draw.line(screen, (0, 0, 0), (data.p[0].x, data.p[0].y), (data.p[1].x, data.p[1].y),2)

		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:		
				sys.exit(0)		

	
	
if __name__ == "__main__":
	main()	