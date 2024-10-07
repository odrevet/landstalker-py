import pygame
import os
import csv

from pytmx.util_pygame import load_pygame

from hero import Hero
from utils import cartesian_to_iso, iso_to_cartesian
from debug import draw_heightmap

class HeightmapCell:
    def __init__(self, height, walkable):
        self.height = height
        self.walkable = walkable

class Heightmap:
    def __init__(self):
        self.left_offset = 0
        self.top_offset = 0
        self.cells = []

    def load(self, map_number):
        map_filename = f"data/Map{map_number}_heightmap.csv"

        if not os.path.exists(map_filename):
            return

        with open(map_filename, mode="r") as file:
            csv_reader = csv.reader(file)
            
            header = next(csv_reader)
            self.left_offset, self.top_offset = int(header[0], 16), int(header[1], 16)

            for row in csv_reader:
                self.cells.append([HeightmapCell(walkable=int(value[0], 16),height=int(value[1], 16)) for value in row])

def load_map(map_number):
    map_filename = f"data/Map{map_number:03d}.tmx"
    if os.path.exists(map_filename):
        return load_pygame(map_filename)
    return None

def draw_map(surface, tiled_map, camera_x, camera_y, hero, heightmap, debug_mode):
    # Draw layers in order
    for layer in tiled_map.visible_layers:
        if hasattr(layer, "data"):
            h_offset = 0
            if hasattr(layer, "offsetx"):
                h_offset = layer.offsetx
            elif "offsetx" in layer.__dict__:
                h_offset = layer.__dict__["offsetx"]
            elif hasattr(layer, "horizontal_offset"):
                h_offset = layer.horizontal_offset

            for y in range(layer.height):
                for x in range(layer.width):
                    tile = layer.data[y][x]
                    if tile:
                        # Get the tile image
                        tile_image = tiled_map.get_tile_image_by_gid(tile)
                        if tile_image:
                            # Convert isometric coordinates to screen coordinates
                            screen_x, screen_y = iso_to_cartesian(
                                x - (tiled_map.width // 2), y - (tiled_map.height // 2), tiled_map.tilewidth, tiled_map.tileheight
                            )
                            if screen_x - camera_x + h_offset > -16 and screen_y - camera_y > -16 and screen_x - camera_x + h_offset < 448 and screen_y - camera_y < 320: 
                                pass

                            # Draw the tile
                            surface.blit(
                                tile_image,
                                (screen_x - camera_x + h_offset, 
                                screen_y - camera_y),
                            )

    # Debug: Draw heightmap
    if debug_mode and heightmap:
        draw_heightmap(surface, heightmap, tiled_map.tilewidth, tiled_map.tileheight, camera_x, camera_y)

    # Draw hero
    hero.draw(surface, debug_mode)