import pygame,sys
from setting import *
from level import Level
from game_data import level_0

pygame.init()

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Pirate Game")
clock = pygame.time.Clock()
level = Level(level_0,screen)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    screen.fill('black')
    level.run()
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()


