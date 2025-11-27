import sys
import argparse
from typing import List, Tuple, Optional

import pygame
import pygame_gui
from pygame_gui.elements.ui_text_box import UITextBox

from hero import Hero
from utils import *
from tiledmap import Tiledmap
from heightmap import Heightmap, HeightmapCell
from debug import draw_hero_boundbox, draw_heightmap, draw_warps

# Constants
DISPLAY_WIDTH: int = 320
DISPLAY_HEIGHT: int = 448
CAMERA_SPEED: int = 5
GRAVITY: int = 2
HERO_SPEED: float = 1.75
HERO_MAX_JUMP: int = 16
FPS: int = 60


class Game:
    def __init__(self, args: argparse.Namespace) -> None:
        pygame.init()
        
        # Display setup
        self.screen: pygame.Surface = pygame.display.set_mode((DISPLAY_HEIGHT, DISPLAY_WIDTH), pygame.RESIZABLE)
        self.surface: pygame.Surface = pygame.Surface((DISPLAY_HEIGHT, DISPLAY_WIDTH))
        pygame.display.set_caption("LandStalker")
        
        # Game state
        self.room_number: int = args.room
        self.debug_mode: bool = args.debug
        self.camera_x: float = 0
        self.camera_y: float = 0
        self.clock: pygame.time.Clock = pygame.time.Clock()
        
        # Debug flags
        self.is_debug_draw_enabled: bool = False
        self.is_height_map_displayed: bool = False
        self.is_boundbox_displayed: bool = False
        self.is_warps_displayed: bool = False
        self.camera_locked: bool = True  # Camera follows hero by default
        
        # Key state tracking for toggles
        self.prev_keys: dict = {}
        
        # GUI setup
        self.manager: pygame_gui.UIManager = pygame_gui.UIManager((800, 600), "ui.json")
        self.hud_textbox: UITextBox = UITextBox(
            "",
            pygame.Rect((0, 0), (450, 36)),
            manager=self.manager,
            object_id="#hud_textbox",
        )
        self.coord_label: pygame_gui.elements.UILabel = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 2), (-1, -1)),
            text="",
            manager=self.manager
        )
        
        # Load room
        self.tiled_map: Tiledmap = Tiledmap()
        self.tiled_map.load(self.room_number)
        room_map: str = self.tiled_map.data.properties['RoomMap']
        
        # Load heightmap
        self.heightmap: Heightmap = Heightmap()
        self.heightmap.load(room_map)
        
        # Create hero
        self.hero: Hero = Hero(args.x, args.y, args.z)
        
        # Validate and fix hero spawn position
        self.fix_hero_spawn_position()
        
        # Center camera on hero initially
        self.center_camera_on_hero()
    
    def fix_hero_spawn_position(self) -> None:
        """Fix hero position if spawned in invalid location"""
        tile_h: int = self.tiled_map.data.tileheight
        
        # Check if hero is out of bounds
        hero_pos = self.hero.get_world_pos()
        hero_tile_x: int = int(hero_pos.x // tile_h)
        hero_tile_y: int = int(hero_pos.y // tile_h)
        
        # If out of bounds or on unwalkable tile, find first walkable tile
        if (hero_tile_x < 0 or hero_tile_y < 0 or
            hero_tile_x >= self.heightmap.get_width() or
            hero_tile_y >= self.heightmap.get_height() or
            not self.heightmap.get_cell(hero_tile_x, hero_tile_y) or
            not self.heightmap.get_cell(hero_tile_x, hero_tile_y).is_walkable()):
            
            # Find first walkable tile
            for y in range(self.heightmap.get_height()):
                for x in range(self.heightmap.get_width()):
                    cell: Optional[HeightmapCell] = self.heightmap.get_cell(x, y)
                    if cell and cell.is_walkable():
                        # Move hero to center of this tile
                        new_x: float = x * tile_h + tile_h // 2
                        new_y: float = y * tile_h + tile_h // 2
                        new_z: float = cell.height * tile_h
                        self.hero.set_world_pos(
                            new_x, new_y, new_z,
                            self.heightmap.left_offset,
                            self.heightmap.top_offset,
                            self.camera_x,
                            self.camera_y
                        )
                        print(f"Hero spawned at invalid position, moved to first walkable tile: ({x}, {y})")
                        return
        
        # Hero is in bounds, check if Z is correct
        cell: Optional[HeightmapCell] = self.heightmap.get_cell(hero_tile_x, hero_tile_y)
        if cell:
            ground_height: float = cell.height * tile_h
            # If hero is below ground, place on ground
            if hero_pos.z < ground_height:
                self.hero.set_world_pos(
                    hero_pos.x, hero_pos.y, ground_height,
                    self.heightmap.left_offset,
                    self.heightmap.top_offset,
                    self.camera_x,
                    self.camera_y
                )
                print(f"Hero was below ground, moved to ground level: Z={ground_height}")
    
    def center_camera_on_hero(self) -> None:
        """Center the camera on the hero's position"""
        self.hero.update_camera(
            self.heightmap.left_offset,
            self.heightmap.top_offset,
            0,  # Use 0,0 for camera to get absolute screen position
            0
        )
        
        # Center camera on hero
        self.camera_x = self.hero._screen_pos.x - DISPLAY_HEIGHT // 2
        self.camera_y = self.hero._screen_pos.y - DISPLAY_WIDTH // 2
        
        # Update hero screen position with new camera
        self.hero.update_camera(
            self.heightmap.left_offset,
            self.heightmap.top_offset,
            self.camera_x,
            self.camera_y
        )
    
    def is_key_just_pressed(self, key: int, keys: pygame.key.ScancodeWrapper) -> bool:
        """Check if a key was just pressed (not held)"""
        was_pressed: bool = self.prev_keys.get(key, False)
        is_pressed: bool = keys[key]
        return is_pressed and not was_pressed
    
    def handle_events(self) -> bool:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            
            self.manager.process_events(event)
        
        return True
    
    def handle_camera_movement(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle manual camera movement with Shift + arrow keys (unlocks camera)"""
        if not keys[pygame.K_LSHIFT]:
            return
        
        # Manual camera control unlocks the camera
        self.camera_locked = False
        
        moved: bool = False
        if keys[pygame.K_LEFT]:
            self.camera_x -= CAMERA_SPEED
            moved = True
        if keys[pygame.K_RIGHT]:
            self.camera_x += CAMERA_SPEED
            moved = True
        if keys[pygame.K_UP]:
            self.camera_y -= CAMERA_SPEED
            moved = True
        if keys[pygame.K_DOWN]:
            self.camera_y += CAMERA_SPEED
            moved = True
        
        if moved:
            self.hero.update_camera(
                self.heightmap.left_offset,
                self.heightmap.top_offset,
                self.camera_x,
                self.camera_y
            )
    
    def check_warp_collision(self) -> bool:
        """Check if hero is colliding with any warp and handle room transition"""
        tile_h: int = self.tiled_map.data.tileheight
        
        # Get hero's bounding box in world coordinates
        hero_pos = self.hero.get_world_pos()
        hero_x: float = hero_pos.x
        hero_y: float = hero_pos.y
        hero_width: int = tile_h
        hero_height: int = tile_h
        
        for warp in self.tiled_map.warps:
            if warp.check_collision(hero_x, hero_y, hero_width, hero_height, tile_h, self.tiled_map.room_number, self.heightmap):
                target_room: int = warp.get_target_room(self.room_number)
                
                if target_room != self.room_number:
                    # Load new room
                    self.room_number = target_room
                    self.tiled_map.load(self.room_number)
                    
                    # Load heightmap for new room
                    room_map: str = self.tiled_map.data.properties['RoomMap']
                    self.heightmap = Heightmap()
                    self.heightmap.load(room_map)
                    
                    # Set hero position to warp destination
                    dest_tile_x: int
                    dest_tile_y: int
                    dest_tile_x, dest_tile_y = warp.get_destination(self.room_number, self.heightmap)
                    
                    # Get current Z or use ground height at destination
                    dest_cell: Optional[HeightmapCell] = self.heightmap.get_cell(dest_tile_x, dest_tile_y)
                    dest_tile_z: int = dest_cell.height

                    self.hero.set_world_pos(
                        dest_tile_x * tile_h, dest_tile_y * tile_h, dest_tile_z * tile_h,
                        self.heightmap.left_offset,
                        self.heightmap.top_offset,
                        self.camera_x,
                        self.camera_y
                    )
                    
                    # Center camera on hero in new room
                    self.camera_locked = True
                    self.center_camera_on_hero()
                    
                    return True
        
        return False
    
    def apply_gravity(self) -> None:
        """Apply gravity to hero"""
        hero_pos = self.hero.get_world_pos()
        height_at_foot: float = hero_pos.z + self.hero.HEIGHT * self.tiled_map.data.tileheight
        
        margin: int = 1
        tile_h: int = self.tiled_map.data.tileheight
        left_x: int = int((hero_pos.x + margin) // tile_h)
        left_y: int = int((hero_pos.y + tile_h) // tile_h)
        bottom_x: int = int((hero_pos.x + tile_h - margin) // tile_h)
        bottom_y: int = int((hero_pos.y + tile_h - margin) // tile_h)
        top_x: int = int((hero_pos.x + margin) // tile_h)
        top_y: int = int((hero_pos.y + margin) // tile_h)
        right_x: int = int((hero_pos.x + tile_h - margin) // tile_h)
        right_y: int = int((hero_pos.y - margin) // tile_h)
        
        # Check if hero is above ground
        if not self.hero.is_jumping:
            cells = self.heightmap.cells
            if (cells[top_y][top_x].height * tile_h < height_at_foot and
                cells[bottom_y][bottom_x].height * tile_h < height_at_foot and
                cells[right_y][right_x].height * tile_h < height_at_foot and
                cells[left_y][left_x].height * tile_h < height_at_foot):
                
                new_z: float = hero_pos.z - 1
                self.hero.set_world_pos(
                    hero_pos.x, hero_pos.y, new_z,
                    self.heightmap.left_offset,
                    self.heightmap.top_offset,
                    self.camera_x,
                    self.camera_y
                )
                
                if self.camera_locked:
                    self.center_camera_on_hero()
                
                self.hero.touch_ground = False
            else:
                self.hero.touch_ground = True
    
    def can_move_to(self, next_x: float, next_y: float, check_cells: List[Tuple[int, int]]) -> bool:
        """Check if hero can move to the given position"""
        hero_pos = self.hero.get_world_pos()
        height_at_foot: float = hero_pos.z + self.hero.HEIGHT * self.tiled_map.data.tileheight
        tile_h: int = self.tiled_map.data.tileheight
        
        for cell_x, cell_y in check_cells:
            cell: Optional[HeightmapCell] = self.heightmap.get_cell(cell_x, cell_y)
            if not cell or not cell.is_walkable():
                return False
            if cell.height * tile_h > height_at_foot:
                return False
        
        return True
    
    def handle_hero_movement(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle hero movement"""
        if keys[pygame.K_LSHIFT]:  # Camera mode
            return
        
        # Re-lock camera when hero moves
        if any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]]):
            self.camera_locked = True
        
        hero_pos = self.hero.get_world_pos()
        tile_h: int = self.tiled_map.data.tileheight
        moved: bool = False
        
        # Calculate current tile positions
        left_x: int = int(hero_pos.x // tile_h)
        left_y: int = int((hero_pos.y + tile_h) // tile_h)
        bottom_x: int = int((hero_pos.x + tile_h) // tile_h)
        bottom_y: int = int((hero_pos.y + tile_h) // tile_h)
        top_x: int = int(hero_pos.x // tile_h)
        top_y: int = int(hero_pos.y // tile_h)
        right_x: int = int((hero_pos.x + tile_h) // tile_h)
        right_y: int = int(hero_pos.y // tile_h)
        
        new_x: float = hero_pos.x
        new_y: float = hero_pos.y
        
        if keys[pygame.K_LEFT]:
            next_x: float = hero_pos.x - HERO_SPEED
            new_top_x: int = int(next_x // tile_h)
            new_left_x: int = int(next_x // tile_h)
            
            if next_x > 0 and self.can_move_to(next_x, hero_pos.y, [
                (new_top_x, top_y), (new_left_x, left_y)
            ]):
                new_x = next_x
                moved = True
        
        elif keys[pygame.K_RIGHT]:
            next_x: float = hero_pos.x + HERO_SPEED
            new_bottom_x: int = int((next_x + tile_h) // tile_h)
            new_right_x: int = int((next_x + tile_h) // tile_h)
            
            if new_right_x < self.heightmap.get_width() and self.can_move_to(
                next_x, hero_pos.y, [(new_bottom_x, bottom_y), (new_right_x, right_y)]
            ):
                new_x = next_x
                moved = True
        
        elif keys[pygame.K_UP]:
            next_y: float = hero_pos.y - HERO_SPEED
            new_top_y: int = int(next_y // tile_h)
            new_right_y: int = int(next_y // tile_h)
            
            if next_y > 0 and self.can_move_to(hero_pos.x, next_y, [
                (top_x, new_top_y), (right_x, new_right_y)
            ]):
                new_y = next_y
                moved = True
        
        elif keys[pygame.K_DOWN]:
            next_y: float = hero_pos.y + HERO_SPEED
            new_left_y: int = int((next_y + tile_h) // tile_h)
            new_bottom_y: int = int((next_y + tile_h) // tile_h)
            
            if new_left_y < self.heightmap.get_height() and self.can_move_to(
                hero_pos.x, next_y, [(left_x, new_left_y), (bottom_x, new_bottom_y)]
            ):
                new_y = next_y
                moved = True
        
        if moved:
            self.hero.set_world_pos(
                new_x, new_y, hero_pos.z,
                self.heightmap.left_offset,
                self.heightmap.top_offset,
                self.camera_x,
                self.camera_y
            )
            
            if self.camera_locked:
                self.center_camera_on_hero()
    
    def handle_jump(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle hero jumping"""
        if keys[pygame.K_SPACE] and self.hero.touch_ground and not self.hero.is_jumping:
            self.hero.is_jumping = True
        
        if self.hero.is_jumping:
            hero_pos = self.hero.get_world_pos()
            if self.hero.current_jump < HERO_MAX_JUMP:
                self.hero.current_jump += 2
                new_z: float = hero_pos.z + 2
                self.hero.set_world_pos(
                    hero_pos.x, hero_pos.y, new_z,
                    self.heightmap.left_offset,
                    self.heightmap.top_offset,
                    self.camera_x,
                    self.camera_y
                )
                
                if self.camera_locked:
                    self.center_camera_on_hero()
            else:
                self.hero.is_jumping = False
                self.hero.current_jump = 0
    
    def handle_debug_toggles(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle debug flag toggles"""
        if self.debug_mode:
            if self.is_key_just_pressed(pygame.K_d, keys):
                self.is_debug_draw_enabled = not self.is_debug_draw_enabled
    
    def handle_room_change(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle room changing with CTRL + arrow keys"""
        if not self.debug_mode:
            return
        
        if not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
            return
        
        room_changed: bool = False
        
        if self.is_key_just_pressed(pygame.K_RIGHT, keys):
            self.room_number += 1
            room_changed = True
        elif self.is_key_just_pressed(pygame.K_LEFT, keys):
            if self.room_number > 1:
                self.room_number -= 1
                room_changed = True
        
        if room_changed:
            self.tiled_map.load(self.room_number)
            self.camera_locked = True
            
            room_map: str = self.tiled_map.data.properties['RoomMap']
            self.heightmap = Heightmap()
            self.heightmap.load(room_map)
            
            self.center_camera_on_hero()
    
    def update_hud(self) -> None:
        """Update HUD with debug information"""
        if self.debug_mode and self.heightmap.cells:
            hero_pos = self.hero.get_world_pos()
            tile_h: int = self.tiled_map.data.tileheight
            world_z: float = hero_pos.z + self.hero.HEIGHT * tile_h
            tile_x: float = hero_pos.x // tile_h
            tile_y: float = hero_pos.y // tile_h
            tile_z: float = world_z // tile_h
            
            camera_status: str = "LOCKED" if self.camera_locked else "FREE"
            
            self.coord_label.set_text(
                f"Room: {self.room_number} | X: {hero_pos.x:.1f}, Y: {hero_pos.y:.1f}, Z: {world_z:.1f} | "
                f"T X: {tile_x:.0f}, Y: {tile_y:.0f}, Z: {tile_z:.0f} | CAM: {camera_status}"
            )
    
    def render(self) -> None:
        """Render the game"""
        self.surface.fill((0, 0, 0))
        
        # Draw map
        self.tiled_map.draw(self.surface, self.camera_x, self.camera_y, self.hero)
        
        # Debug rendering
        if self.debug_mode and self.is_debug_draw_enabled:
            draw_heightmap(
                self.surface,
                self.heightmap,
                self.tiled_map.data.tileheight,
                self.camera_x,
                self.camera_y
            )
            
            draw_hero_boundbox(
                self.hero,
                self.surface,
                self.tiled_map.data.tileheight,
                self.camera_x,
                self.camera_y,
                self.heightmap.left_offset,
                self.heightmap.top_offset
            )
            
            draw_warps(
                self.surface,
                self.tiled_map.warps,
                self.heightmap,
                self.tiled_map.data.tileheight,
                self.camera_x,
                self.camera_y,
                self.room_number
            )
        
        # Draw GUI
        self.manager.draw_ui(self.surface)
        
        # Scale and display
        scaled_surface: pygame.Surface = pygame.transform.scale(self.surface, self.screen.get_size())
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop"""
        running: bool = True
        
        while running:
            time_delta: float = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            running = self.handle_events()
            if not running:
                break
            
            # Get key states
            keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
            
            # Exit on Escape
            if keys[pygame.K_ESCAPE]:
                break
            
            # Handle input
            self.handle_camera_movement(keys)
            self.handle_debug_toggles(keys)
            self.handle_room_change(keys)
            
            if not keys[pygame.K_LSHIFT]:
                self.apply_gravity()
                self.handle_hero_movement(keys)
                self.handle_jump(keys)
                self.check_warp_collision()  # Check for warps after movement
            
            # Update
            self.update_hud()
            self.manager.update(time_delta)
            
            # Render
            self.render()
            
            # Store current key states for next frame
            self.prev_keys = {k: keys[k] for k in [pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT]}
        
        pygame.quit()
        sys.exit()


def main() -> None:
    # Initialize argument parser
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="LandStalker Game")
    parser.add_argument('-r', '--room', type=int, default=1, help='Room number')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-x', type=int, default=0, help='Hero starting X position')
    parser.add_argument('-y', type=int, default=0, help='Hero starting Y position')
    parser.add_argument('-z', type=int, default=0, help='Hero starting Z position')
    
    args: argparse.Namespace = parser.parse_args()
    
    # Create and run game
    game: Game = Game(args)
    game.run()


if __name__ == "__main__":
    main()