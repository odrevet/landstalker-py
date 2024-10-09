import pygame
from pygame.math import Vector2, Vector3
from utils import cartesian_to_iso

def draw_heightmap(screen, heightmap, tile_width, tile_height, camera_x, camera_y):
    offset_x = (heightmap.left_offset - 12) * tile_height - 12
    offset_y = (heightmap.top_offset - 11) * tile_height - 12
    
    for y, row in enumerate(heightmap.cells):
        for x, cell in enumerate(row):
            if cell.walkable >= 4:
                continue
                
            height = cell.height
            left_x, left_y = cartesian_to_iso(
                x * tile_height - offset_x, 
                y * tile_height + tile_height - offset_y
            )
            bottom_x, bottom_y = cartesian_to_iso(
                x * tile_height + tile_height - offset_x,
                y * tile_height + tile_height - offset_y,
            )
            top_x, top_y = cartesian_to_iso(x * tile_height - offset_x, y * tile_height - offset_y)
            right_x, right_y = cartesian_to_iso(
                x * tile_height + tile_height - offset_x, y * tile_height - offset_y
            )

            # top
            points = [
                (left_x - camera_x, left_y - camera_y - height * tile_height),
                (bottom_x - camera_x, bottom_y - camera_y - height * tile_height),
                (right_x - camera_x, right_y - camera_y - height * tile_height),
                (top_x - camera_x, top_y - camera_y - height * tile_height),
            ]

            color = (255, 255, 255)
            if height == 0:
                color = (255, 255, 0)
            elif height >= 20: 
                color = (255, 0, 0)

            pygame.draw.lines(screen, color, True, points)

            # front
            if x < len(heightmap.cells[0]) - 1 and heightmap.cells[y][x + 1].height < height: 
                height_diff = heightmap.cells[y][x + 1].height - height
                pygame.draw.line(screen, 
                                 (200, 255, 200), 
                                 (bottom_x - camera_x, bottom_y - camera_y - height * tile_height), 
                                 (bottom_x - camera_x, bottom_y - camera_y - height * tile_height - height_diff * tile_height))
                pygame.draw.line(screen, 
                                 (200, 255, 200), 
                                 (right_x - camera_x, right_y - camera_y - height * tile_height), 
                                 (right_x - camera_x, right_y - camera_y - height * tile_height - height_diff * tile_height))

            # left
            if y < len(heightmap.cells) - 1 and heightmap.cells[y + 1][x].height < height: 
                height_diff = heightmap.cells[y + 1][x].height - height
                pygame.draw.line(screen, 
                                 (200, 155, 200), 
                                 (bottom_x - camera_x, bottom_y - camera_y - height * tile_height), 
                                 (bottom_x - camera_x, bottom_y - camera_y - height * tile_height - height_diff * tile_height))

def draw_hero_boundbox(hero, screen,  tile_height):
    left_x, left_y = cartesian_to_iso(hero.world_pos.x , hero.world_pos.y + tile_height)
    bottom_x, bottom_y = cartesian_to_iso(hero.world_pos.x + tile_height, hero.world_pos.y + tile_height)
    top_x, top_y = cartesian_to_iso(hero.world_pos.x, hero.world_pos.y)
    right_x, right_y = cartesian_to_iso(hero.world_pos.x + tile_height, hero.world_pos.y)

    # top
    points = [(left_x, left_y - hero.world_pos.z),
            (bottom_x, bottom_y - hero.world_pos.z),
            (right_x, right_y - hero.world_pos.z),
            (top_x, top_y - hero.world_pos.z)]

    pygame.draw.lines(screen,
                    (255, 25, 25),
                    True,
                    points)

    # bottom
    points = [(left_x, left_y - hero.world_pos.z + hero.HEIGHT * tile_height),
            (bottom_x, bottom_y - hero.world_pos.z + hero.HEIGHT * tile_height),
            (right_x, right_y - hero.world_pos.z + hero.HEIGHT * tile_height),
            (top_x, top_y - hero.world_pos.z + hero.HEIGHT * tile_height)]

    pygame.draw.lines(
        screen,
        (255, 25, 25),
        True,
        points,
    )
