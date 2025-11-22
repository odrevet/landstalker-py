import pygame

from pytmx.util_pygame import load_pygame
from pygame.math import Vector2

from hero import Hero
from utils import cartesian_to_iso, iso_to_cartesian

class Tile:
    def __init__(self, offset):
        self.image = None
        self.has_priority = False
        self.is_hflipped = False
        self.is_vflipped = False
        self.offset = Vector2(offset[0], offset[1])

    def draw(self, surface, screen_pos, layer_offset_h, camera_x, camera_y):
        surface.blit(self.image, 
                    (screen_pos.x - camera_x + self.offset.x + layer_offset_h, 
                     screen_pos.y - camera_y + self.offset.y))

class Blockset:
    def __init__(self):
        self.tiles = []
        self.grid_pos = None
        self.screen_pos = None
        self.gid = None

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

    def load(self, room_number):
        tmx_filename = f"data/rooms/Room{room_number:03d}.tmx"
        self.data = load_pygame(tmx_filename)

        self.background_layer = Layer()
        self.background_layer.data = self.data.get_layer_by_name("Background")
        self.populate_layer(self.background_layer)

        self.foreground_layer = Layer()
        self.foreground_layer.data = self.data.get_layer_by_name("Foreground")
        self.populate_layer(self.foreground_layer)

        warps = []
        for warp in self.data.get_layer_by_name('Warps'):
            warp_data = {
                'room1': int(warp.properties['room1']),
                'room2': int(warp.properties['room2']),
                'x': warp.x,
                'y': warp.y,
                'x2': int(warp.properties['x2']),
                'y2': int(warp.properties['y2']),
                'width': warp.width,
                'height': warp.height,
                'type': warp.properties['warpType']
            }
            print(warp_data)
            warps.append(warp_data)


        
    def draw(self, surface, camera_x, camera_y, hero):
        self.background_layer.draw(surface, camera_x, camera_y)

        for blockset in self.foreground_layer.blocksets:
            for tile in blockset.tiles:
                if tile.has_priority == False:
                    tile.draw(surface, blockset.screen_pos, self.foreground_layer.data.offsetx, camera_x, camera_y)

        hero.draw(surface)
        
        for blockset in self.foreground_layer.blocksets:
            for tile in blockset.tiles:
                if tile.has_priority == True:
                    tile.draw(surface, blockset.screen_pos, self.foreground_layer.data.offsetx, camera_x, camera_y)

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
                blockset.grid_pos = Vector2(x, y)
                blockset.screen_pos = Vector2(screen_x, screen_y)
                blockset.gid = gid

                # Access the tile properties
                tile_properties = self.data.get_tile_properties_by_gid(gid)

                for index, (sub_tile, offset) in enumerate(zip(tiles_rect, offsets)):
                    tile = Tile(offset)
                    tile.image = tile_image.subsurface(sub_tile)

                    tile.is_hflipped = tile_properties.get(f"isHFlipped{index}", False)
                    tile.is_vflipped = tile_properties.get(f"isVFlipped{index}", False)
                    tile.has_priority = tile_properties.get(f"hasPriority{index}", False)

                    blockset.tiles.append(tile)
                layer.blocksets.append(blockset)
