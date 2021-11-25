import pygame
from pygame import transform

from support import import_csv_layout, import_cut_graphics
from setting import tile_size
from tile import Tile,StaticTile,Crate,AnimatedTile,Coin,Palm
from enemies import Enemy
from decoration import *
from player import Player
from particles import ParticlesEffect
from game_data import levels

class Level:
    def __init__(self,current_level,surface,create_overworld):
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None
               

        # Overworld connection:
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']
        

        # player:
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)
        
        # dust:
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False
        
        # terrain:
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')
        
        # grass:
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout,'grass')
        
        # crates:
        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprites = self.create_tile_group(crates_layout,'crates')
        
        # coin:
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout,'coins')
        
        # foreground palms:
        fg_palm_layout = import_csv_layout(level_data['fg palms'])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout,'fg palms')
        
        # background palms:
        bg_palm_layout = import_csv_layout(level_data['bg palms'])
        self.bg_palm_sprites = self.create_tile_group(fg_palm_layout,'bg palms')
        
        # enemies:
        enemies_layout = import_csv_layout(level_data['enemies'])
        self.enemies_sprites = self.create_tile_group(enemies_layout,'enemies')
        
        # constraint:
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout,'constraint')
        
        # decoration:
        # sky:
        self.sky = Sky(8)
        
        # water:
        level_width = len(terrain_layout[0])*tile_size
        self.water = Water(screen_height - 20,level_width)
        
        # cloud:
        self.clouds = Clouds(400,level_width,30)
    
    def create_tile_group(self,layout,type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size
                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('graphics\\terrain\\terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                        
                    if type == 'grass':
                        grass_tile_list = import_cut_graphics('graphics\\decoration\\grass\\grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)

                    if type == 'crates':
                        sprite = Crate(tile_size,x,y)
                    
                    if type == 'coins':
                        if val == '0':
                            sprite = Coin(tile_size,x,y,'graphics\\coins\\gold')
                        if val == '1':
                            sprite = Coin(tile_size,x,y,'graphics\\coins\\silver')

                    if type == 'fg palms':
                        if val == '0':
                            sprite = Palm(tile_size,x,y,'graphics\\terrain\\palm_small',38)
                        if val == '1':
                            sprite = Palm(tile_size,x,y,'graphics\\terrain\\palm_large',64)
                        
                    if type == 'bg palms':
                        sprite = Palm(tile_size,x,y,'graphics\\terrain\\palm_bg',64)

                    if type == 'enemies':
                        sprite = Enemy(tile_size,x,y)
                    
                    if type == 'constraint':
                        sprite = Tile(tile_size,x,y)
                    
                    sprite_group.add(sprite)                    

        
        return sprite_group

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x,y),self.display_surface,self.create_jump_particles)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load('graphics\\character\\hat.png').convert_alpha()
                    sprite = StaticTile(tile_size,x,y,hat_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy,self.constraint_sprites,False):
                enemy.reverse()

    def create_jump_particles(self,pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,5)
        else:
            pos += pygame.math.Vector2(10,-5)
        jump_particle_sprite = ParticlesEffect(pos,'jump')
        self.dust_sprite.add(jump_particle_sprite) 
    
    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        diretion_x = player.direction.x

        if player_x < screen_width / 4 and diretion_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - screen_width / 4 and diretion_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            player.speed = 8
            self.world_shift = 0

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        collidable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.fg_palm_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right
        
        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):        
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(-10,15)
            fall_dust_particle = ParticlesEffect(self.player.sprite.rect.midbottom - offset,'land')
            self.dust_sprite.add(fall_dust_particle)

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level,0)
    
    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite,self.goal,False):
            self.create_overworld(self.current_level,self.new_max_level)

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.fg_palm_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
        
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
           player.on_ceiling = False

    def run(self):
        # run:
        # decoration:
        # sky:
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface,self.world_shift)        
        
        # bg palms
        self.bg_palm_sprites.update(self.world_shift)
        self.bg_palm_sprites.draw(self.display_surface)
        
        # terrain:
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)
        
        # glass:
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)
        
        # enemies:
        self.enemies_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemies_sprites.draw(self.display_surface)
        
        # crates:
        self.crates_sprites.update(self.world_shift)
        self.crates_sprites.draw(self.display_surface)
            
        # coins:
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)
        
        # fg palms:
        self.fg_palm_sprites.update(self.world_shift)
        self.fg_palm_sprites.draw(self.display_surface)
        
        # dust particles:
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)
        
        # player setup:
        self.player.update()
        self.horizontal_movement_collision()
        
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
        
        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        
        self.check_death()
        self.check_win()

        # water:
        self.water.draw(self.display_surface,self.world_shift)
        
        
