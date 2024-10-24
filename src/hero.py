import pygame
from pygame.math import Vector2, Vector3
from utils import cartesian_to_iso

class Hero(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0, z=0):
        super().__init__()
        self.image = pygame.image.load('data/gfx/SpriteGfx000Anim000.png').convert_alpha()

        self._world_pos = Vector3(x, y, z)
        self.screen_pos = Vector2()

        self.HEIGHT = 2   # height in tile
        self.touch_ground = False
        self.is_jumping = False
        self.current_jump = 0

    def update_screen_pos(self, heightmap_left_offset, heightmap_top_offset, camera_x, camera_y):
        offset_x = (heightmap_left_offset - 12 + 4) * 16
        offset_y = (heightmap_top_offset - 11 + 4) * 16

        iso_x, iso_y = cartesian_to_iso(self._world_pos.x - offset_x, self._world_pos.y - offset_y)
        self.screen_pos.x = iso_x - 16 - camera_x
        self.screen_pos.y = iso_y - self._world_pos.z + 12 - camera_y 

    def draw(self, surface):
        surface.blit(self.image, self.screen_pos)
