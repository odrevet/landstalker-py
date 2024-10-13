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

    def draw(self, surface, camera_x, camera_y, hero):
        # draw background layer
        background_layer = self.data.get_layer_by_name("Background")
        self.draw_background(surface, background_layer, camera_x, camera_y)

        # draw foreground layer
        foreground_layer = self.data.get_layer_by_name("Foreground")
        self.draw_foreground(surface, foreground_layer, camera_x, camera_y)

        # draw hero
        hero.draw(surface)

    def draw_background(self, surface, background_layer, camera_x, camera_y):
        if hasattr(background_layer, "data"):
            h_offset = 0
            if hasattr(background_layer, "offsetx"):
                h_offset = background_layer.offsetx
            elif "offsetx" in background_layer.__dict__:
                h_offset = background_layer.__dict__["offsetx"]
            elif hasattr(background_layer, "horizontal_offset"):
                h_offset = background_layer.horizontal_offset

        for y in range(background_layer.height):
            for x in range(background_layer.width):
                tile = background_layer.data[y][x]
                # Get the tile image
                tile_image = self.data.get_tile_image_by_gid(tile)

                # Convert isometric coordinates to screen coordinates
                screen_x, screen_y = iso_to_cartesian(x, y)
                screen_x *= self.data.tilewidth // 2
                screen_y *= self.data.tileheight // 2

                #if screen_x - camera_x > -16 and screen_y - camera_y > -16 and screen_x - camera_x < 448 and screen_y - camera_y < 320:
                # Draw the tile
                surface.blit(
                    tile_image,
                    (screen_x - camera_x + h_offset, 
                    screen_y - camera_y),
                )

    def draw_foreground(self, surface, foreground_layer, camera_x, camera_y):
        for y in range(foreground_layer.height):
            for x in range(foreground_layer.width):
                tile = foreground_layer.data[y][x]
                # Get the tile image
                tile_image = self.data.get_tile_image_by_gid(tile)
                # Get the tile dimensions
                tile_width, tile_height = tile_image.get_width(), tile_image.get_height()

                # Define sub-rects for each quadrant of the tile
                top_left_rect = pygame.Rect(0, 0, tile_width // 2, tile_height // 2)
                top_right_rect = pygame.Rect(tile_width // 2, 0, tile_width // 2, tile_height // 2)
                bottom_left_rect = pygame.Rect(0, tile_height // 2, tile_width // 2, tile_height // 2)
                bottom_right_rect = pygame.Rect(tile_width // 2, tile_height // 2, tile_width // 2, tile_height // 2)

                # Convert isometric coordinates to screen coordinates
                screen_x, screen_y = iso_to_cartesian(x, y)
                screen_x *= self.data.tilewidth // 2
                screen_y *= self.data.tileheight // 2

                # Define offsets for the sub-tiles
                offsets = [(0, 0), (tile_width // 2, 0), (0, tile_height // 2), (tile_width // 2, tile_height // 2)]
                sub_tiles = [top_left_rect, top_right_rect, bottom_left_rect, bottom_right_rect]

                # Blit each sub-tile
                for sub_tile, offset in zip(sub_tiles, offsets):
                    sub_image = tile_image.subsurface(sub_tile)
                    surface.blit(
                        sub_image,
                        (screen_x - camera_x + offset[0],
                        screen_y - camera_y + offset[1]),
                    )