import sys
import argparse

import pygame
import pygame_gui
from pygame_gui.elements.ui_text_box import UITextBox

from hero import Hero
from utils import *
from tiledmap import Tiledmap
from heightmap import Heightmap
from debug import draw_hero_boundbox, draw_heightmap

# Constants
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 448
CAMERA_SPEED = 5
GRAVITY = 2
HERO_SPEED = 1.75
HERO_MAX_JUMP = 16
FPS = 60


class Game:
    def __init__(self, args):
        pygame.init()
        
        # Display setup
        self.screen = pygame.display.set_mode((DISPLAY_HEIGHT, DISPLAY_WIDTH), pygame.RESIZABLE)
        self.surface = pygame.Surface((DISPLAY_HEIGHT, DISPLAY_WIDTH))
        pygame.display.set_caption("LandStalker")
        
        # Game state
        self.room_number = args.room
        self.debug_mode = args.debug
        self.camera_x, self.camera_y = 0, 0
        self.clock = pygame.time.Clock()
        
        # Debug flags
        self.is_height_map_displayed = False
        self.is_boundbox_displayed = False
        
        # Key state tracking for toggles
        self.prev_keys = {}
        
        # GUI setup
        self.manager = pygame_gui.UIManager((800, 600), "ui.json")
        self.hud_textbox = UITextBox(
            "",
            pygame.Rect((0, 0), (450, 36)),
            manager=self.manager,
            object_id="#hud_textbox",
        )
        self.coord_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 2), (-1, -1)),
            text="",
            manager=self.manager
        )
        
        # Load room
        self.tiled_map = Tiledmap()
        self.tiled_map.load(self.room_number)
        
        # Load heightmap from tilemap properties
        self.heightmap = Heightmap()
        self.heightmap.load_from_tilemap(self.tiled_map)
        
        # Create hero
        self.hero = Hero(args.x, args.y, args.z)
        self.hero.update_screen_pos(
            self.heightmap.left_offset,
            self.heightmap.top_offset,
            self.camera_x,
            self.camera_y
        )
    
    def is_key_just_pressed(self, key, keys):
        """Check if a key was just pressed (not held)"""
        was_pressed = self.prev_keys.get(key, False)
        is_pressed = keys[key]
        return is_pressed and not was_pressed
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            
            self.manager.process_events(event)
        
        return True
    
    def handle_camera_movement(self, keys):
        """Handle camera movement with Shift + arrow keys"""
        if not keys[pygame.K_LSHIFT]:
            return
        
        moved = False
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
            self.hero.update_screen_pos(
                self.heightmap.left_offset,
                self.heightmap.top_offset,
                self.camera_x,
                self.camera_y
            )
    
    def apply_gravity(self):
        """Apply gravity to hero"""
        height_at_foot = self.hero._world_pos.z + self.hero.HEIGHT * self.tiled_map.data.tileheight
        
        tile_h = self.tiled_map.data.tileheight
        left_x = int(self.hero._world_pos.x // tile_h)
        left_y = int((self.hero._world_pos.y + tile_h) // tile_h)
        bottom_x = int((self.hero._world_pos.x + tile_h) // tile_h)
        bottom_y = int((self.hero._world_pos.y + tile_h) // tile_h)
        top_x = int(self.hero._world_pos.x // tile_h)
        top_y = int(self.hero._world_pos.y // tile_h)
        right_x = int((self.hero._world_pos.x + tile_h) // tile_h)
        right_y = int(self.hero._world_pos.y // tile_h)
        
        # Check if hero is above ground
        if not self.hero.is_jumping:
            cells = self.heightmap.cells
            if (cells[top_y][top_x].height * tile_h < height_at_foot and
                cells[bottom_y][bottom_x].height * tile_h < height_at_foot and
                cells[right_y][right_x].height * tile_h < height_at_foot and
                cells[left_y][left_x].height * tile_h < height_at_foot):
                
                self.hero._world_pos.z -= 1
                self.hero.update_screen_pos(
                    self.heightmap.left_offset,
                    self.heightmap.top_offset,
                    self.camera_x,
                    self.camera_y
                )
                self.hero.touch_ground = False
            else:
                self.hero.touch_ground = True
    
    def can_move_to(self, next_x, next_y, check_cells):
        """Check if hero can move to the given position"""
        height_at_foot = self.hero._world_pos.z + self.hero.HEIGHT * self.tiled_map.data.tileheight
        tile_h = self.tiled_map.data.tileheight
        
        for cell_x, cell_y in check_cells:
            cell = self.heightmap.get_cell(cell_x, cell_y)
            if not cell or not cell.is_walkable():
                return False
            if cell.height * tile_h > height_at_foot:
                return False
        
        return True
    
    def handle_hero_movement(self, keys):
        """Handle hero movement"""
        if keys[pygame.K_LSHIFT]:  # Camera mode
            return
        
        tile_h = self.tiled_map.data.tileheight
        moved = False
        
        # Calculate current tile positions
        left_x = int(self.hero._world_pos.x // tile_h)
        left_y = int((self.hero._world_pos.y + tile_h) // tile_h)
        bottom_x = int((self.hero._world_pos.x + tile_h) // tile_h)
        bottom_y = int((self.hero._world_pos.y + tile_h) // tile_h)
        top_x = int(self.hero._world_pos.x // tile_h)
        top_y = int(self.hero._world_pos.y // tile_h)
        right_x = int((self.hero._world_pos.x + tile_h) // tile_h)
        right_y = int(self.hero._world_pos.y // tile_h)
        
        if keys[pygame.K_LEFT]:
            next_x = self.hero._world_pos.x - HERO_SPEED
            new_top_x = int(next_x // tile_h)
            new_left_x = int(next_x // tile_h)
            
            if next_x > 0 and self.can_move_to(next_x, self.hero._world_pos.y, [
                (new_top_x, top_y), (new_left_x, left_y)
            ]):
                self.hero._world_pos.x = next_x
                moved = True
        
        elif keys[pygame.K_RIGHT]:
            next_x = self.hero._world_pos.x + HERO_SPEED
            new_bottom_x = int((next_x + tile_h) // tile_h)
            new_right_x = int((next_x + tile_h) // tile_h)
            
            if new_right_x < self.heightmap.get_width() and self.can_move_to(
                next_x, self.hero._world_pos.y, [(new_bottom_x, bottom_y), (new_right_x, right_y)]
            ):
                self.hero._world_pos.x = next_x
                moved = True
        
        elif keys[pygame.K_UP]:
            next_y = self.hero._world_pos.y - HERO_SPEED
            new_top_y = int(next_y // tile_h)
            new_right_y = int(next_y // tile_h)
            
            if next_y > 0 and self.can_move_to(self.hero._world_pos.x, next_y, [
                (top_x, new_top_y), (right_x, new_right_y)
            ]):
                self.hero._world_pos.y = next_y
                moved = True
        
        elif keys[pygame.K_DOWN]:
            next_y = self.hero._world_pos.y + HERO_SPEED
            new_left_y = int((next_y + tile_h) // tile_h)
            new_bottom_y = int((next_y + tile_h) // tile_h)
            
            if new_left_y < self.heightmap.get_height() and self.can_move_to(
                self.hero._world_pos.x, next_y, [(left_x, new_left_y), (bottom_x, new_bottom_y)]
            ):
                self.hero._world_pos.y = next_y
                moved = True
        
        if moved:
            self.hero.update_screen_pos(
                self.heightmap.left_offset,
                self.heightmap.top_offset,
                self.camera_x,
                self.camera_y
            )
    
    def handle_jump(self, keys):
        """Handle hero jumping"""
        if keys[pygame.K_SPACE] and self.hero.touch_ground and not self.hero.is_jumping:
            self.hero.is_jumping = True
        
        if self.hero.is_jumping:
            if self.hero.current_jump < HERO_MAX_JUMP:
                self.hero.current_jump += 2
                self.hero._world_pos.z += 2
                self.hero.update_screen_pos(
                    self.heightmap.left_offset,
                    self.heightmap.top_offset,
                    self.camera_x,
                    self.camera_y
                )
            else:
                self.hero.is_jumping = False
                self.hero.current_jump = 0
    
    def handle_debug_toggles(self, keys):
        """Handle debug flag toggles"""
        if self.debug_mode:
            if self.is_key_just_pressed(pygame.K_h, keys):
                self.is_height_map_displayed = not self.is_height_map_displayed
            
            if self.is_key_just_pressed(pygame.K_b, keys):
                self.is_boundbox_displayed = not self.is_boundbox_displayed
    
    def handle_room_change(self, keys):
        """Handle room changing with CTRL + arrow keys"""
        if not self.debug_mode:
            return
        
        if not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
            return
        
        room_changed = False
        
        if self.is_key_just_pressed(pygame.K_RIGHT, keys):
            self.room_number += 1
            room_changed = True
        elif self.is_key_just_pressed(pygame.K_LEFT, keys):
            if self.room_number > 1:
                self.room_number -= 1
                room_changed = True
        
        if room_changed:
            self.tiled_map.load(self.room_number)
            self.camera_x, self.camera_y = 0, 0
            
            # Reload heightmap from new tilemap
            self.heightmap = Heightmap()
            self.heightmap.load_from_tilemap(self.tiled_map)
            
            self.hero.update_screen_pos(
                self.heightmap.left_offset,
                self.heightmap.top_offset,
                self.camera_x,
                self.camera_y
            )
    
    def update_hud(self):
        """Update HUD with debug information"""
        if self.debug_mode and self.heightmap.cells:
            tile_h = self.tiled_map.data.tileheight
            world_z = self.hero._world_pos.z + self.hero.HEIGHT * tile_h
            tile_x = self.hero._world_pos.x // tile_h
            tile_y = self.hero._world_pos.y // tile_h
            tile_z = world_z // tile_h
            
            self.coord_label.set_text(
                f"X: {self.hero._world_pos.x:.1f}, Y: {self.hero._world_pos.y:.1f}, Z: {world_z:.1f} | "
                f"T X: {tile_x:.0f}, Y: {tile_y:.0f}, Z: {tile_z:.0f}"
            )
    
    def render(self):
        """Render the game"""
        self.surface.fill((0, 0, 0))
        
        # Draw map
        self.tiled_map.draw(self.surface, self.camera_x, self.camera_y)
        
        # Draw hero
        self.hero.draw(self.surface)
        
        # Debug rendering
        if self.debug_mode:
            if self.is_height_map_displayed:
                draw_heightmap(
                    self.surface,
                    self.heightmap,
                    self.tiled_map.data.tileheight,
                    self.camera_x,
                    self.camera_y
                )
            
            if self.is_boundbox_displayed:
                draw_hero_boundbox(
                    self.hero,
                    self.surface,
                    self.tiled_map.data.tileheight,
                    self.camera_x,
                    self.camera_y,
                    self.heightmap.left_offset,
                    self.heightmap.top_offset
                )
        
        # Draw GUI
        self.manager.draw_ui(self.surface)
        
        # Scale and display
        scaled_surface = pygame.transform.scale(self.surface, self.screen.get_size())
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            time_delta = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            running = self.handle_events()
            if not running:
                break
            
            # Get key states
            keys = pygame.key.get_pressed()
            
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
            
            # Update
            self.update_hud()
            self.manager.update(time_delta)
            
            # Render
            self.render()
            
            # Store current key states for next frame
            self.prev_keys = {k: keys[k] for k in [pygame.K_h, pygame.K_b, pygame.K_LEFT, pygame.K_RIGHT]}
        
        pygame.quit()
        sys.exit()


def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="LandStalker Game")
    parser.add_argument('-r', '--room', type=int, default=1, help='Room number')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-x', type=int, default=0, help='Hero starting X position')
    parser.add_argument('-y', type=int, default=0, help='Hero starting Y position')
    parser.add_argument('-z', type=int, default=0, help='Hero starting Z position')
    
    args = parser.parse_args()
    
    # Create and run game
    game = Game(args)
    game.run()


if __name__ == "__main__":
    main()