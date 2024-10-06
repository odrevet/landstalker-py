import pygame
from pygame.math import Vector2, Vector3
from utils import cartesian_to_iso

class Hero(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0, z=0):
        super().__init__()
        self.image = pygame.image.load('export/SpriteGfx000Frame01.png').convert_alpha()

        self.world_pos = Vector3(x, y, z)
        self.__screen_pos = Vector2()
        self.update_screen_pos()

        self.HEIGHT = 2   # height in tile

    def update_screen_pos(self):
        iso_x, iso_y = cartesian_to_iso(self.world_pos.x, self.world_pos.y)
        self.__screen_pos.x = iso_x - 16
        self.__screen_pos.y = iso_y - self.world_pos.z

    def draw(self, surface, debug_mode):
        surface.blit(self.image, self.__screen_pos)