import pygame, sys
from pygame.locals import *
from setting import *
from level import Level

# pygame setup:
pygame.init()

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Mighty Action X')
clock = pygame.time.Clock()
level = Level(level_map,screen)
# run screen:
run = True
while run:
    for event in pygame.event.get(): 
        if event.type == QUIT:
            run = False
    
    screen.fill('black')
    level.run()

    pygame.display.update()
    clock.tick(60)
    

pygame.quit()
sys.exit()

