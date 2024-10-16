import os
import csv 

import pygame

from pytmx.util_pygame import load_pygame
from pygame.math import Vector2

from hero import Hero
from utils import cartesian_to_iso, iso_to_cartesian
from debug import draw_heightmap

import xml.etree.ElementTree as ET

class Tile:
    def __init__(self, offset):
        self.image = None
        self.flags = None
        self.offset = Vector2(offset[0], offset[1])

    def draw(self, surface, screen_pos, layer_offset_h, camera_x, camera_y):
        surface.blit(self.image, 
                    (screen_pos.x - camera_x + self.offset.x + layer_offset_h, 
                     screen_pos.y - camera_y + self.offset.y))

class Blockset:
    def __init__(self):
        self.tiles = []
        self.screen_pos = None
        self.gid = None
        self.csv_value = None

    def draw(self, surface, layer_offset_h, camera_x, camera_y):
        if self.screen_pos.x - camera_x + layer_offset_h > -16 and \
           self.screen_pos.y - camera_y > -16 and \
           self.screen_pos.x - camera_x + layer_offset_h < 448 and \
           self.screen_pos.y - camera_y < 320:
            for tile in self.tiles:
                tile.draw(surface, self.screen_pos, layer_offset_h, camera_x, camera_y)

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
        tmx_filename = f"data/Map{map_number:03d}.tmx"
        self.data = load_pygame(tmx_filename)

        self.background_layer = Layer()
        self.background_layer.data = self.data.get_layer_by_name("Background")
        self.populate_layer(self.background_layer)

        self.foreground_layer = Layer()
        self.foreground_layer.data = self.data.get_layer_by_name("Foreground")
        self.populate_layer(self.foreground_layer)

        self.set_csv_values(tmx_filename)

        blocktile_name, palette = self.data.tilesets[0].name.rsplit('_', 1)
        blocktile_filename = f"data/{blocktile_name}.csv"

        if os.path.exists(blocktile_filename):
            self.set_flags(self.background_layer, blocktile_filename)
            self.set_flags(self.foreground_layer, blocktile_filename)

    def set_flags(self, layer, filename):
        with open(filename, mode="r") as file:
            csv_reader = csv.reader(file)

            row_index = 0
            for row in csv_reader:
                for blockset in layer.blocksets:
                    if blockset.csv_value == row_index:
                        for tile_index, flags in enumerate(row):
                            blockset.tiles[tile_index].flags = flags
                row_index += 1

    def set_csv_values(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        
        for layer in root.findall(".//layer"):
            layer_name = layer.get('name')
            data = layer.find('data').text.strip().split(',')
            
            csv_values = [int(value) for value in data]
            
            if layer_name == "Background":
                for index, csv_value in enumerate(csv_values):
                    self.background_layer.blocksets[index].csv_value = csv_value
            elif layer_name == "Foreground":
                for index, csv_value in enumerate(csv_values):
                    self.foreground_layer.blocksets[index].csv_value = csv_value
        
    def draw(self, surface, camera_x, camera_y, hero):
        self.background_layer.draw(surface, camera_x, camera_y)
        self.foreground_layer.draw(surface, camera_x, camera_y)
        hero.draw(surface)


    def populate_layer(self, layer):
        for y in range(layer.data.height):
            for x in range(layer.data.width):
                gid = layer.data.data[y][x]

                # Get the tile image
                tile_image = self.data.get_tile_image_by_gid(gid)
                
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
                blockset.gid = gid
                for sub_tile, offset in zip(tiles_rect, offsets):
                    tile = Tile(offset)
                    tile.image = tile_image.subsurface(sub_tile)
                    blockset.tiles.append(tile)
                
                layer.blocksets.append(blockset)
