import os

import pygame

from pytmx.util_pygame import load_pygame
from pygame.math import Vector2

from hero import Hero
from utils import cartesian_to_iso, iso_to_cartesian
from debug import draw_heightmap

class Tile:
    def __init__(self, offset):
        self.image = None
        self.data = None
        self.flags = None
        self.offset = Vector2(offset[0], offset[1])

class Blockset:
    def __init__(self):
        self.tiles = []
        self.screen_pos = None
        self.palette = None

    def draw(self, surface, layer_offset_h, camera_x, camera_y):
        for tile in self.tiles:
            surface.blit(tile.image, 
                    (self.screen_pos.x - camera_x + tile.offset.x + layer_offset_h, self.screen_pos.y - camera_y + tile.offset.y))

class Layer:
    def __init__(self):
        self.data = None
        self.blocksets = []

    def draw(self, surface, camera_x, camera_y):
        for blockset in self.blocksets:
            blockset.draw(surface, self.data.offsetx, camera_x, camera_y)


class Tiledmap:
    def __init__(self):
        self.data = None
        self.background_layer = None
        self.foreground_layer = None

    def load(self, map_number):
        self.data = load_pygame(f"data/Map{map_number:03d}.tmx")

        self.background_layer = Layer()
        self.background_layer.data = self.data.get_layer_by_name("Background")
        self.populate_layer(self.background_layer)

        self.foreground_layer = Layer()
        self.foreground_layer.data = self.data.get_layer_by_name("Foreground")
        self.populate_layer(self.foreground_layer)

#    def load_flags(self, filename):
#        with open(filename, mode="r") as file:
#            csv_reader = csv.reader(file)
#
#            for row in csv_reader:
#                for index, flags in enumerate(row):
#                    self.blocksets[index].flags = flags

    def draw(self, surface, camera_x, camera_y, hero):
        self.background_layer.draw(surface, camera_x, camera_y)
        self.foreground_layer.draw(surface, camera_x, camera_y)
        hero.draw(surface)


    def populate_layer(self, layer):
        for y in range(layer.data.height):
            for x in range(layer.data.width):
                layer_data = layer.data.data[y][x]

                # Get the tile image
                tile_image = self.data.get_tile_image_by_gid(layer_data)
                
                # Get the tile dimensions
                tile_width, tile_height = tile_image.get_width(), tile_image.get_height()

                # Define sub-rects for each quadrant of the tile
                top_left_rect = pygame.Rect(0, 0, tile_width // 2, tile_height // 2)
                top_right_rect = pygame.Rect(tile_width // 2, 0, tile_width // 2, tile_height // 2)
                bottom_left_rect = pygame.Rect(0, tile_height // 2, tile_width // 2, tile_height // 2)
                bottom_right_rect = pygame.Rect(tile_width // 2, tile_height // 2, tile_width // 2, tile_height // 2)

                # Define offsets for the tiles inside a block
                offsets = [(0, 0), (tile_width // 2, 0), (0, tile_height // 2), (tile_width // 2, tile_height // 2)]
                tiles_rect = [top_left_rect, top_right_rect, bottom_left_rect, bottom_right_rect]

                # Calculate screen position of the block
                screen_x, screen_y = iso_to_cartesian(x, y)
                screen_x *= self.data.tilewidth // 2
                screen_y *= self.data.tileheight // 2

                # instanciate a new blockset
                blockset = Blockset()
                blockset.screen_pos = Vector2(screen_x, screen_y)
                for sub_tile, offset in zip(tiles_rect, offsets):
                    tile = Tile(offset)
                    tile.data = layer_data
                    tile.image = tile_image.subsurface(sub_tile)
                    blockset.tiles.append(tile)
                
                layer.blocksets.append(blockset)
