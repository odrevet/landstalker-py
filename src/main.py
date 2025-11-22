import sys
import argparse

import pygame
import pygame_gui
from pygame_gui.elements.ui_text_box import UITextBox

from hero import Hero
from utils import *
from tiledmap import Tiledmap
from heightmap import Heightmap
from debug import draw_hero_boundbox, draw_heightmap, is_height_map_displayed, is_boundbox_displayed

# pygame
pygame.init()
display_width = 320
display_height = 448
screen = pygame.display.set_mode((display_height, display_width), pygame.RESIZABLE)
surface = pygame.Surface((display_height, display_width))

pygame.display.set_caption("LandStalker")

# Initialize the argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument('-r', '--room', type=int, default=1, help='room number')
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
parser.add_argument('-x', type=int, default=0)
parser.add_argument('-y', type=int, default=0)
parser.add_argument('-z', type=int, default=0)

# Parse arguments
args = parser.parse_args()

# Use the arguments
room_number = args.room
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
GRAVITY = 2
HERO_SPEED = 1.75
HERO_MAX_JUMP = 16

# Room
tiled_map = Tiledmap()
tiled_map.load(room_number)

#room_map = tiled_map.data.properties['RoomMap']

# Heightmap
#heightmap = Heightmap()
#heightmap.load(room_map)

# Hero
#hero = Hero(args.x, args.y, args.z)
#hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

while True:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LSHIFT]:
        # Check arrow keys for camera movement
        if keys[pygame.K_LEFT]:
            camera_x -= CAMERA_SPEED
            #hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
        if keys[pygame.K_RIGHT]:
            camera_x += CAMERA_SPEED
            #hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
        if keys[pygame.K_UP]:
            camera_y -= CAMERA_SPEED
            #hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
        if keys[pygame.K_DOWN]:
            camera_y += CAMERA_SPEED
            #hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
#    else:
#        height_at_foot = hero._world_pos.z + hero.HEIGHT * tiled_map.data.tileheight
#
#        left_x = int(hero._world_pos.x // tiled_map.data.tileheight) 
#        left_y = int((hero._world_pos.y + tiled_map.data.tileheight) // tiled_map.data.tileheight)
#
#        bottom_x = int((hero._world_pos.x + tiled_map.data.tileheight) // tiled_map.data.tileheight)
#        bottom_y = int((hero._world_pos.y + tiled_map.data.tileheight) // tiled_map.data.tileheight)
#
#        top_x = int(hero._world_pos.x // tiled_map.data.tileheight)
#        top_y = int(hero._world_pos.y // tiled_map.data.tileheight)
#
#        right_x = int((hero._world_pos.x + tiled_map.data.tileheight) // tiled_map.data.tileheight)
#        right_y = int(hero._world_pos.y // tiled_map.data.tileheight)
#
#        # Gravity
#        if hero.is_jumping == False \
#        and heightmap.cells[top_y][top_x].height * tiled_map.data.tileheight < height_at_foot \
#        and heightmap.cells[bottom_y][bottom_x].height * tiled_map.data.tileheight < height_at_foot \
#        and heightmap.cells[right_y][right_x].height * tiled_map.data.tileheight < height_at_foot \
#        and heightmap.cells[left_y][left_x].height * tiled_map.data.tileheight < height_at_foot:
#            hero._world_pos.z -= 1
#            hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
#            hero.touch_ground = False
#        else:
#            hero.touch_ground = True
#
#        # Hero movement
#        if keys[pygame.K_LEFT]:
#            next_x = hero._world_pos.x - HERO_SPEED
#            
#            top_x = int(next_x // tiled_map.data.tileheight)
#            left_x = int(next_x // tiled_map.data.tileheight) 
#
#            top_cell = heightmap.get_cell(top_x,top_y)
#            left_cell = heightmap.get_cell(left_x, left_y)
#
#            if next_x > 0\
#            and top_cell.is_walkable() \
#            and top_cell.height * tiled_map.data.tileheight <= height_at_foot \
#            and left_cell.is_walkable() \
#            and left_cell.height * tiled_map.data.tileheight <= height_at_foot:
#                hero._world_pos.x -= HERO_SPEED
#                hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
#        elif keys[pygame.K_RIGHT]:
#            next_x = hero._world_pos.x + HERO_SPEED
#
#            bottom_x = int((next_x + tiled_map.data.tileheight) // tiled_map.data.tileheight)
#            right_x = int((next_x + tiled_map.data.tileheight) // tiled_map.data.tileheight)
#
#            if right_x < heightmap.get_width():
#                bottom_cell = heightmap.cells[bottom_y][bottom_x]
#                right_cell = heightmap.cells[right_y][right_x]
#
#                if bottom_cell.is_walkable() \
#                and bottom_cell.height * tiled_map.data.tileheight <= height_at_foot \
#                and right_cell.is_walkable() \
#                and right_cell.height * tiled_map.data.tileheight <= height_at_foot:
#                    hero._world_pos.x += HERO_SPEED
#                    hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
#        elif keys[pygame.K_UP]:
#            next_y = hero._world_pos.y - HERO_SPEED
#
#            top_y = int(next_y // tiled_map.data.tileheight)
#            right_y = int(next_y // tiled_map.data.tileheight)
#
#            top_cell = heightmap.get_cell(top_x, top_y)
#            right_cell = heightmap.get_cell(right_x, right_y)
#
#            if next_y > 0 \
#            and top_cell.is_walkable() \
#            and top_cell.height * tiled_map.data.tileheight <= height_at_foot \
#            and right_cell.is_walkable() \
#            and right_cell.height * tiled_map.data.tileheight <= height_at_foot:
#                hero._world_pos.y = next_y
#                hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
#        elif keys[pygame.K_DOWN]:
#            next_y = hero._world_pos.y + HERO_SPEED
#
#            left_y = int((next_y + tiled_map.data.tileheight) // tiled_map.data.tileheight)
#            bottom_y = int((next_y + tiled_map.data.tileheight) // tiled_map.data.tileheight)
#
#            if left_y < heightmap.get_height():
#                left_cell = heightmap.get_cell(left_x, left_y)
#                bottom_cell = heightmap.get_cell(bottom_x, bottom_y)
#
#                if left_cell.is_walkable() \
#                and left_cell.height * tiled_map.data.tileheight <= height_at_foot \
#                and bottom_cell.is_walkable() \
#                and bottom_cell.height * tiled_map.data.tileheight <= height_at_foot:
#                    hero._world_pos.y += HERO_SPEED
#                    hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
#        elif keys[pygame.K_h]:
#            is_height_map_displayed = not is_height_map_displayed
#        elif keys[pygame.K_b]:
#            is_boundbox_displayed = not is_boundbox_displayed
#
#
#    if keys[pygame.K_SPACE] and hero.touch_ground == True and hero.is_jumping == False:
#        hero.is_jumping = True
#
#    if hero.is_jumping:
#        if hero.current_jump < HERO_MAX_JUMP:
#            hero.current_jump += 2
#            next_z = hero._world_pos.z + 2
#            hero._world_pos.z = next_z
#            hero.update_screen_pos(heightmap.left_offset, heightmap.top_offset, camera_x, camera_y)
#        else:
#            hero.is_jumping = False
#
    # Exit on Escape key
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    # Handle map changing with CTRL + arrow keys
    if debug_mode and keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
        if keys[pygame.K_RIGHT]:
            room_number += 1
            tiled_map.load(room_number)

            camera_x, camera_y = 0, 0  # Reset camera when changing maps

            #heightmap = Heightmap()
            #heightmap.load(room_number)

        elif keys[pygame.K_LEFT]:
            if room_number > 1:
                room_number -= 1
                tiled_map.load(room_number)

                camera_x, camera_y = 0, 0  # Reset camera when changing maps

                #heightmap = Heightmap()
                #heightmap.load(room_number)


    # Clear the screen
    surface.fill((0, 0, 0))

    # Draw the map
    tiled_map.draw(surface, camera_x, camera_y)

    # Draw heightmap (debug)
    #if debug_mode and is_height_map_displayed:
    #    draw_heightmap(surface, heightmap, tiled_map.data.tileheight, camera_x, camera_y)


    # Update HUD with debug info
#    if debug_mode and heightmap.cells:
#        coord_label.set_text(f"X: {hero._world_pos.x}, Y: {hero._world_pos.y}, Z: {hero._world_pos.z + hero.HEIGHT * tiled_map.data.tileheight}\
#T X: {hero._world_pos.x // tiled_map.data.tileheight}, Y: {hero._world_pos.y // tiled_map.data.tileheight}, Z: {(hero._world_pos.z + hero.HEIGHT * tiled_map.data.tileheight)// tiled_map.data.tileheight}")


    #if debug_mode and is_boundbox_displayed:
    #    draw_hero_boundbox(hero, surface, tiled_map.data.tileheight, camera_x, camera_y, heightmap.left_offset, heightmap.top_offset)

    manager.draw_ui(surface)

    # Update the display
    manager.update(time_delta)

    scaled_surface = pygame.transform.scale(surface, screen.get_size())
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
