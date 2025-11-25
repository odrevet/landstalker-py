import pygame
from utils import cartesian_to_iso


# -------------------------------------------------------------
#  DRAW HEIGHTMAP
# -------------------------------------------------------------
def draw_heightmap(screen, heightmap, tile_height, camera_x, camera_y):
    """Draw the isometric heightmap with semi-transparent fills and wireframe."""

    offset_x = (heightmap.left_offset - 12) * tile_height - 12
    offset_y = (heightmap.top_offset - 11) * tile_height - 12

    # Create a temporary surface for transparency
    temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    for y, row in enumerate(heightmap.cells):
        for x, cell in enumerate(row):

            height = cell.height

            # Compute four corners of tile
            left_x, left_y = cartesian_to_iso(
                x * tile_height - offset_x,
                y * tile_height + tile_height - offset_y
            )
            bottom_x, bottom_y = cartesian_to_iso(
                x * tile_height + tile_height - offset_x,
                y * tile_height + tile_height - offset_y,
            )
            top_x, top_y = cartesian_to_iso(
                x * tile_height - offset_x, 
                y * tile_height - offset_y
            )
            right_x, right_y = cartesian_to_iso(
                x * tile_height + tile_height - offset_x,
                y * tile_height - offset_y
            )

            # Height-shifted (top face)
            points = [
                (left_x - camera_x,  left_y  - camera_y - height * tile_height),
                (bottom_x - camera_x, bottom_y - camera_y - height * tile_height),
                (right_x - camera_x, right_y - camera_y - height * tile_height),
                (top_x - camera_x,   top_y   - camera_y - height * tile_height),
            ]

            # Choose color by conditions
            if cell.walkable >= 4:
                # Non-walkable - red
                outline_color = (255, 80, 80)
                fill_color = (255, 80, 80, 80)
            elif height == 0:
                # Ground level - yellow
                outline_color = (255, 255, 120)
                fill_color = (255, 255, 120, 60)
            elif height >= 20:
                # Very high - light red
                outline_color = (255, 120, 120)
                fill_color = (255, 120, 120, 70)
            else:
                # Normal walkable - white/blue
                outline_color = (255, 255, 255)
                fill_color = (200, 200, 255, 50)

            # Draw filled polygon with transparency
            if len(points) >= 3:
                pygame.draw.polygon(temp_surface, fill_color, points)
            
            # Draw outline
            pygame.draw.lines(screen, outline_color, True, points, 1)

            # Draw vertical edges if tile in front or below is lower
            if x < len(heightmap.cells[0]) - 1:
                neighbor_h = heightmap.cells[y][x + 1].height
                if neighbor_h < height:
                    hdiff = neighbor_h - height
                    
                    # Front face points
                    front_points = [
                        (bottom_x - camera_x, bottom_y - camera_y - height * tile_height),
                        (bottom_x - camera_x, bottom_y - camera_y - neighbor_h * tile_height),
                        (right_x - camera_x, right_y - camera_y - neighbor_h * tile_height),
                        (right_x - camera_x, right_y - camera_y - height * tile_height),
                    ]
                    
                    # Draw filled face
                    face_color = (outline_color[0], outline_color[1], outline_color[2], 40)
                    pygame.draw.polygon(temp_surface, face_color, front_points)
                    
                    # Draw edges
                    pygame.draw.line(screen, outline_color,
                        (bottom_x - camera_x, bottom_y - camera_y - height * tile_height),
                        (bottom_x - camera_x, bottom_y - camera_y - neighbor_h * tile_height)
                    )
                    pygame.draw.line(screen, outline_color,
                        (right_x - camera_x, right_y - camera_y - height * tile_height),
                        (right_x - camera_x, right_y - camera_y - neighbor_h * tile_height)
                    )

            if y < len(heightmap.cells) - 1:
                neighbor_h = heightmap.cells[y + 1][x].height
                if neighbor_h < height:
                    hdiff = neighbor_h - height
                    
                    # Side face points
                    side_points = [
                        (bottom_x - camera_x, bottom_y - camera_y - height * tile_height),
                        (bottom_x - camera_x, bottom_y - camera_y - neighbor_h * tile_height),
                        (left_x - camera_x, left_y - camera_y - neighbor_h * tile_height),
                        (left_x - camera_x, left_y - camera_y - height * tile_height),
                    ]
                    
                    # Draw filled face
                    face_color = (outline_color[0], outline_color[1], outline_color[2], 30)
                    pygame.draw.polygon(temp_surface, face_color, side_points)
                    
                    # Draw edge
                    pygame.draw.line(screen, outline_color,
                        (bottom_x - camera_x, bottom_y - camera_y - height * tile_height),
                        (bottom_x - camera_x, bottom_y - camera_y - neighbor_h * tile_height)
                    )
    
    # Blit the transparent surface onto the main screen
    screen.blit(temp_surface, (0, 0))


# -------------------------------------------------------------
#  DRAW HERO BOUNDING BOX
# -------------------------------------------------------------
def draw_hero_boundbox(hero, screen, tile_height, camera_x, camera_y, left_offset, top_offset):
    """Draw hero's isometric bounding box."""

    offset_x = (left_offset - 12 + 4) * tile_height - 12
    offset_y = (top_offset - 11 + 4) * tile_height - 12

    # Corners of the hero footprint
    left_x, left_y = cartesian_to_iso(hero._world_pos.x - offset_x, hero._world_pos.y + tile_height - offset_y)
    bottom_x, bottom_y = cartesian_to_iso(hero._world_pos.x + tile_height - offset_x, hero._world_pos.y + tile_height - offset_y)
    top_x, top_y = cartesian_to_iso(hero._world_pos.x - offset_x, hero._world_pos.y - offset_y)
    right_x, right_y = cartesian_to_iso(hero._world_pos.x + tile_height - offset_x, hero._world_pos.y - offset_y)

    z_top = hero._world_pos.z - hero.HEIGHT * tile_height
    z_bottom = hero._world_pos.z + hero.HEIGHT * tile_height - hero.HEIGHT * tile_height
    color = (50, 255, 50)

    # Top rectangle
    pygame.draw.lines(
        screen, color, True,
        [
            (left_x  - camera_x, left_y  - camera_y - z_top),
            (bottom_x - camera_x, bottom_y - camera_y - z_top),
            (right_x - camera_x, right_y - camera_y - z_top),
            (top_x   - camera_x, top_y   - camera_y - z_top),
        ]
    )

    # Bottom rectangle
    pygame.draw.lines(
        screen, color, True,
        [
            (left_x  - camera_x, left_y  - camera_y - z_bottom),
            (bottom_x - camera_x, bottom_y - camera_y - z_bottom),
            (right_x - camera_x, right_y - camera_y - z_bottom),
            (top_x   - camera_x, top_y   - camera_y - z_bottom),
        ]
    )


# -------------------------------------------------------------
#  DRAW WARPS
# -------------------------------------------------------------
def draw_warps(screen, warps, heightmap, tile_h, camera_x, camera_y, current_room):
    """Draw all warps for debugging"""
    
    # Precompute offsets
    off_x = (heightmap.left_offset) * tile_h
    off_y = (heightmap.top_offset) * tile_h
    
    def iso_point(wx, wy):
        """Convert world Cartesian → isometric pixel coords."""
        ix, iy = cartesian_to_iso(wx - off_x, wy - off_y)
        return ix - camera_x, iy - camera_y
    
    font = pygame.font.SysFont("Arial", 10)
    
    for warp in warps:
        x = 0
        y = 0

        if warp.room1 == current_room:
            x = warp.x
            y = warp.y
        else:
            x = warp.x2
            y = warp.y2

        
        color = (0, 200, 255)

        # Warp rectangle corners (already in pixel coordinates from Tiled)
        p1 = iso_point(x * tile_h, y * tile_h)
        p2 = iso_point(x  * tile_h + warp.width  * tile_h, y * tile_h)
        p3 = iso_point(x  * tile_h+ warp.width * tile_h, y * tile_h + warp.height * tile_h)
        p4 = iso_point(x * tile_h, y  * tile_h+ warp.height * tile_h)
    
        # Draw warp zone rectangle
        pygame.draw.lines(screen, color, True, [p1, p2, p3, p4])
        
        # Main label
        label = f"{warp.room1}→{warp.room2}"
        text_surf = font.render(label, True, color)
        screen.blit(text_surf, (p1[0] + 2, p1[1] - 12))
        
        # Position and size info
        pos_label = f"({x},{y}) {warp.width}x{warp.height}"
        pos_surf = font.render(pos_label, True, (150, 150, 255))
        screen.blit(pos_surf, (p1[0] + 2, p1[1] + 2))