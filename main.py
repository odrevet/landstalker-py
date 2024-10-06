import sys
import argparse

import pygame
import pygame_gui
from pygame_gui.elements.ui_text_box import UITextBox

from hero import Hero
from utils import *
from map import *
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

# Hero
hero = Hero(args.x, args.y, args.z)

coord_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 2), (-1, -1)), text="", manager=manager
)

camera_x, camera_y = 0, 0
CAMERA_SPEED = 5

# Load the initial TMX map
tiled_map = load_map(current_map_number)
left_offset, top_offset, height_map = load_heightmap(current_map_number)

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

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
    elif height_map:
        height_at_foot = hero.world_pos.z + hero.HEIGHT * tiled_map.tileheight

        map_height = len(height_map) * tiled_map.tileheight
        map_width = len(height_map[0]) * tiled_map.tileheight

        left_x = int(hero.world_pos.x // tiled_map.tileheight) 
        left_y = int((hero.world_pos.y + tiled_map.tileheight) // tiled_map.tileheight)

        bottom_x = int((hero.world_pos.x + tiled_map.tileheight) // tiled_map.tileheight)
        bottom_y = int((hero.world_pos.y + tiled_map.tileheight) // tiled_map.tileheight)

        top_x = int(hero.world_pos.x // tiled_map.tileheight)
        top_y = int(hero.world_pos.y // tiled_map.tileheight)

        right_x = int((hero.world_pos.x + tiled_map.tileheight) // tiled_map.tileheight)
        right_y = int(hero.world_pos.y // tiled_map.tileheight)

        # Gravity
        if height_map[top_y][top_x] * tiled_map.tileheight < height_at_foot \
        and height_map[bottom_y][bottom_x] * tiled_map.tileheight < height_at_foot \
        and height_map[right_y][right_x] * tiled_map.tileheight < height_at_foot \
        and height_map[left_y][left_x] * tiled_map.tileheight < height_at_foot:
            hero.world_pos.z -= 1
            hero.update_screen_pos()

        # Hero movement
        if keys[pygame.K_LEFT]:
            next_x = hero.world_pos.x - 1
            
            top_x = int(next_x // tiled_map.tileheight)
            left_x = int(next_x // tiled_map.tileheight) 

            if next_x > 0\
            and height_map[top_y][top_x] * tiled_map.tileheight <= height_at_foot \
            and height_map[left_y][left_x] * tiled_map.tileheight <= height_at_foot:
                hero.world_pos.x -= 1
                hero.update_screen_pos()
        elif keys[pygame.K_RIGHT]:
            next_x = hero.world_pos.x + 1

            bottom_x = int((next_x + tiled_map.tileheight) // tiled_map.tileheight)
            right_x = int((next_x + tiled_map.tileheight) // tiled_map.tileheight)

            if next_x < map_width\
            and height_map[bottom_y][bottom_x] * tiled_map.tileheight <= height_at_foot \
            and height_map[right_y][right_x] * tiled_map.tileheight <= height_at_foot:
                hero.world_pos.x += 1
                hero.update_screen_pos()
        elif keys[pygame.K_UP]:
            next_y = hero.world_pos.y - 1

            top_y = int(next_y // tiled_map.tileheight)
            right_y = int(next_y // tiled_map.tileheight)

            if next_y > 0 \
            and height_map[top_y][top_x] * tiled_map.tileheight <= height_at_foot \
            and height_map[right_y][right_x] * tiled_map.tileheight <= height_at_foot:
                hero.world_pos.y = next_y
                hero.update_screen_pos()
        elif keys[pygame.K_DOWN]:
            next_y = hero.world_pos.y + 1

            left_y = int((next_y + tiled_map.tileheight) // tiled_map.tileheight)
            bottom_y = int((next_y + tiled_map.tileheight) // tiled_map.tileheight)

            if next_y < map_height\
            and height_map[left_y][left_x] * tiled_map.tileheight <= height_at_foot \
            and height_map[bottom_y][bottom_x] * tiled_map.tileheight <= height_at_foot:
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
            current_map_number += 1
            new_map = load_map(current_map_number)
            if new_map:
                tiled_map = new_map
                camera_x, camera_y = 0, 0  # Reset camera when changing maps
                print(f"Loaded Map{current_map_number:03d}.tmx")
                left_offset, top_offset, height_map = load_heightmap(current_map_number)
            else:
                current_map_number -= 1
                print(
                    f"No more maps available. Staying on Map{current_map_number:03d}.tmx"
                )
        elif keys[pygame.K_LEFT]:
            if current_map_number > 1:
                current_map_number -= 1
                tiled_map = load_map(current_map_number)
                camera_x, camera_y = 0, 0  # Reset camera when changing maps
                print(f"Loaded Map{current_map_number:03d}.tmx")
                left_offset, top_offset, height_map = load_heightmap(current_map_number)
            else:
                print("Already at the first map.")

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the map
    draw_map(screen, tiled_map, camera_x, camera_y, hero, height_map, left_offset, top_offset, debug_mode)

    # Update HUD with debug info
    if debug_mode and height_map:
        coord_label.set_text(f"X: {hero.world_pos.x}, Y: {hero.world_pos.y}, Z: {hero.world_pos.z + hero.HEIGHT * tiled_map.tileheight}\
T X: {hero.world_pos.x // tiled_map.tileheight}, Y: {hero.world_pos.y // tiled_map.tileheight}, Z: {(hero.world_pos.z + hero.HEIGHT * tiled_map.tileheight)// tiled_map.tileheight}")


    if debug_mode:
        draw_hero_boundbox(hero, screen, tiled_map.tileheight)

    manager.draw_ui(screen)

    # Update the display
    manager.update(time_delta)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
