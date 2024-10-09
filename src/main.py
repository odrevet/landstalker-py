import sys
import argparse

import pygame
import pygame_gui
from pygame_gui.elements.ui_text_box import UITextBox

from hero import Hero
from utils import *
from tiledmap import Tiledmap
from heightmap import Heightmap
from debug import draw_hero_boundbox

# pygame
pygame.init()
display_width = 320
display_height = 448
screen = pygame.display.set_mode((display_height, display_width))
pygame.display.set_caption("LandStalker")

# Initialize the argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument('-m', '--map', type=int, default=1, help='Map number')
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
parser.add_argument('-x', type=int, default=0)
parser.add_argument('-y', type=int, default=0)
parser.add_argument('-z', type=int, default=0)

# Parse arguments
args = parser.parse_args()

# Use the arguments
current_map_number = args.map
debug_mode = args.debug

# gui
manager = pygame_gui.UIManager((800, 600), "ui.json")
hud_textbox = UITextBox(
            "",
            pygame.Rect((0, 0), (450, 36)),
            manager=manager,
            object_id="#hud_textbox",
        )

coord_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 2), (-1, -1)), text="", manager=manager
)

# Camera
camera_x, camera_y = 0, 0
CAMERA_SPEED = 5

# Hero
hero = Hero(args.x, args.y, args.z)

# maps
tiled_map = Tiledmap()
tiled_map.load(current_map_number)

heightmap = Heightmap() 
heightmap.load(current_map_number)

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

extra_left = -12
extra_top = -11

while True:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if debug_mode and keys[pygame.K_LSHIFT]:
        # Check arrow keys for camera movement
        if keys[pygame.K_LEFT]:
            camera_x -= CAMERA_SPEED
        if keys[pygame.K_RIGHT]:
            camera_x += CAMERA_SPEED
        if keys[pygame.K_UP]:
            camera_y -= CAMERA_SPEED
        if keys[pygame.K_DOWN]:
            camera_y += CAMERA_SPEED
    elif len(heightmap.cells) > 0:
        height_at_foot = hero.world_pos.z + hero.HEIGHT * tiled_map.data.tileheight

        map_height = len(heightmap.cells) * tiled_map.data.tileheight
        map_width = len(heightmap.cells[0]) * tiled_map.data.tileheight

        left_x = int(hero.world_pos.x // tiled_map.data.tileheight) 
        left_y = int((hero.world_pos.y + tiled_map.data.tileheight) // tiled_map.data.tileheight)

        bottom_x = int((hero.world_pos.x + tiled_map.data.tileheight) // tiled_map.data.tileheight)
        bottom_y = int((hero.world_pos.y + tiled_map.data.tileheight) // tiled_map.data.tileheight)

        top_x = int(hero.world_pos.x // tiled_map.data.tileheight)
        top_y = int(hero.world_pos.y // tiled_map.data.tileheight)

        right_x = int((hero.world_pos.x + tiled_map.data.tileheight) // tiled_map.data.tileheight)
        right_y = int(hero.world_pos.y // tiled_map.data.tileheight)

        # Gravity
        if heightmap.cells[top_y][top_x].height * tiled_map.data.tileheight < height_at_foot \
        and heightmap.cells[bottom_y][bottom_x].height * tiled_map.data.tileheight < height_at_foot \
        and heightmap.cells[right_y][right_x].height * tiled_map.data.tileheight < height_at_foot \
        and heightmap.cells[left_y][left_x].height * tiled_map.data.tileheight < height_at_foot:
            hero.world_pos.z -= 1
            hero.update_screen_pos()

        # Hero movement
        if keys[pygame.K_LEFT]:
            next_x = hero.world_pos.x - 1
            
            top_x = int(next_x // tiled_map.data.tileheight)
            left_x = int(next_x // tiled_map.data.tileheight) 

            if next_x > 0\
            and heightmap.cells[top_y][top_x].height * tiled_map.data.tileheight <= height_at_foot \
            and heightmap.cells[left_y][left_x].height * tiled_map.data.tileheight <= height_at_foot:
                hero.world_pos.x -= 1
                hero.update_screen_pos()
        elif keys[pygame.K_RIGHT]:
            next_x = hero.world_pos.x + 1

            bottom_x = int((next_x + tiled_map.data.tileheight) // tiled_map.data.tileheight)
            right_x = int((next_x + tiled_map.data.tileheight) // tiled_map.data.tileheight)

            if next_x < map_width\
            and heightmap.cells[bottom_y][bottom_x].height * tiled_map.data.tileheight <= height_at_foot \
            and heightmap.cells[right_y][right_x].height * tiled_map.data.tileheight <= height_at_foot:
                hero.world_pos.x += 1
                hero.update_screen_pos()
        elif keys[pygame.K_UP]:
            next_y = hero.world_pos.y - 1

            top_y = int(next_y // tiled_map.data.tileheight)
            right_y = int(next_y // tiled_map.data.tileheight)

            if next_y > 0 \
            and heightmap.cells[top_y][top_x].height * tiled_map.data.tileheight <= height_at_foot \
            and heightmap.cells[right_y][right_x].height * tiled_map.data.tileheight <= height_at_foot:
                hero.world_pos.y = next_y
                hero.update_screen_pos()
        elif keys[pygame.K_DOWN]:
            next_y = hero.world_pos.y + 1

            left_y = int((next_y + tiled_map.data.tileheight) // tiled_map.data.tileheight)
            bottom_y = int((next_y + tiled_map.data.tileheight) // tiled_map.data.tileheight)

            if next_y < map_height\
            and heightmap.cells[left_y][left_x].height * tiled_map.data.tileheight <= height_at_foot \
            and heightmap.cells[bottom_y][bottom_x].height * tiled_map.data.tileheight <= height_at_foot:
                hero.world_pos.y += 1
                hero.update_screen_pos()
        elif keys[pygame.K_SPACE]:
            next_z = hero.world_pos.z + 16
            hero.world_pos.z = next_z
            hero.update_screen_pos()

    # Exit on Escape key
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()




    # Handle map changing with CTRL + arrow keys
    if debug_mode and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
        if keys[pygame.K_RIGHT]:
            if keys[pygame.K_LSHIFT]:
                heightmap.left_offset -= 1
                extra_left -= 1
            else:
                current_map_number += 1
                tiled_map.load(current_map_number)

                camera_x, camera_y = 0, 0  # Reset camera when changing maps

                heightmap = Heightmap()
                heightmap.load(current_map_number)

        elif keys[pygame.K_LEFT]:
            if keys[pygame.K_LSHIFT]:
                heightmap.left_offset += 1
                extra_left += 1
            else:
               if current_map_number > 1:
                   current_map_number -= 1
                   tiled_map.load(current_map_number)

                   camera_x, camera_y = 0, 0  # Reset camera when changing maps

                   heightmap = Heightmap()
                   heightmap.load(current_map_number)
        elif keys[pygame.K_UP]:
            heightmap.top_offset += 1
            extra_top += 1
        elif keys[pygame.K_DOWN]:
            heightmap.top_offset -= 1
            extra_top -= 1

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the map
    tiled_map.draw(screen, camera_x, camera_y, hero, heightmap, debug_mode)

    # Update HUD with debug info
    if debug_mode and heightmap.cells:
#        coord_label.set_text(f"X: {hero.world_pos.x}, Y: {hero.world_pos.y}, Z: {hero.world_pos.z + hero.HEIGHT * tiled_map.data.tileheight}\
#T X: {hero.world_pos.x // tiled_map.data.tileheight}, Y: {hero.world_pos.y // tiled_map.data.tileheight}, Z: {(hero.world_pos.z + hero.HEIGHT * tiled_map.data.tileheight)// tiled_map.data.tileheight}")

        coord_label.set_text(f"l {heightmap.left_offset} ({extra_left}) t {heightmap.top_offset} ({extra_top}) h {heightmap.get_height()} w {heightmap.get_width()}")


    if debug_mode:
        draw_hero_boundbox(hero, screen, tiled_map.data.tileheight)

    manager.draw_ui(screen)

    # Update the display
    manager.update(time_delta)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
