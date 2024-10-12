import os

import pygame

from pytmx.util_pygame import load_pygame

from hero import Hero
from utils import cartesian_to_iso, iso_to_cartesian
from debug import draw_heightmap

class Tiledmap:
    def __init__(self):
        self.data = None

    def load(self, map_number):
        self.data = load_pygame(f"data/Map{map_number:03d}.tmx")

    def draw(self, surface, camera_x, camera_y, hero, heightmap, debug_mode):
        # Draw layers in order
        for layer in self.data.visible_layers:
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
                            tile_image = self.data.get_tile_image_by_gid(tile)
                            if tile_image:
                                # Convert isometric coordinates to screen coordinates
                                screen_x, screen_y = iso_to_cartesian(x, y)

                                screen_x *= self.data.tilewidth // 2
                                screen_y *= self.data.tileheight // 2

                                if screen_x - camera_x + h_offset > -16 and screen_y - camera_y > -16 and screen_x - camera_x + h_offset < 448 and screen_y - camera_y < 320:
                                    # Draw the tile
                                    surface.blit(
                                        tile_image,
                                        (screen_x - camera_x + h_offset, 
                                        screen_y - camera_y),
                                    )

        # Debug: Draw heightmap
        if debug_mode and heightmap:
            draw_heightmap(surface, heightmap, self.data.tileheight, camera_x, camera_y)

        # Draw hero
        hero.draw(surface)