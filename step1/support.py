import pygame
from pygame import surface
from pygame.locals import *
from os import walk

def import_folder(path):
    surface_list = []
    for _,__,img_file in walk(path):
        for img in img_file:
            full_path = path + '\\' + img
            image_surf = pygame.image.load(full_path).convert_alpha()
            # test for exaid:
            # image_img = pygame.image.load(full_path).convert_alpha()
            # image_surf = pygame.Surface((55,65),flags= SRCALPHA)
            # image_surf.blit(image_img,(0,0),pygame.Rect(0,0,55,75))
            # test for exaid:
            surface_list.append(image_surf)
    
    return surface_list
