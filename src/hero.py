import pygame
from pygame.math import Vector2, Vector3
from utils import cartesian_to_iso

class Hero(pygame.sprite.Sprite):
    def __init__(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        super().__init__()
        # Try to load image, create placeholder if it doesn't exist
        try:
            full_image = pygame.image.load('data/gfx/SpriteGfx000Anim001.png').convert_alpha()
            self.image: pygame.Surface = full_image #.subsurface(pygame.Rect(0, 0, 32, 56))
        except (pygame.error, FileNotFoundError):
            # Create a simple placeholder surface if image doesn't exist
            self.image: pygame.Surface = pygame.Surface((32, 56), pygame.SRCALPHA)
            self.image.fill((255, 0, 255, 128))  # Semi-transparent magenta placeholder
        
        self._world_pos: Vector3 = Vector3(x, y, z)
        self._screen_pos: Vector2 = Vector2()
        self.HEIGHT: int = 2   # height in tile
        self.touch_ground: bool = False
        self.is_jumping: bool = False
        self.current_jump: int = 0
        
        # Cache for update_screen_pos parameters
        self._heightmap_left_offset: int = 0
        self._heightmap_top_offset: int = 0
        self._camera_x: float = 0
        self._camera_y: float = 0
    
    def get_world_pos(self) -> Vector3:
        """Get the hero's world position"""
        return self._world_pos
    
    def set_world_pos(self, x: float, y: float, z: float, 
                      heightmap_left_offset: int, heightmap_top_offset: int, 
                      camera_x: float, camera_y: float) -> None:
        """Set the hero's world position and update screen position
        
        Args:
            x, y, z: World coordinates
            heightmap_left_offset: Heightmap left offset
            heightmap_top_offset: Heightmap top offset
            camera_x: Camera X position
            camera_y: Camera Y position
        """
        self._world_pos.x = x
        self._world_pos.y = y
        self._world_pos.z = z
        self._update_screen_pos(heightmap_left_offset, heightmap_top_offset, camera_x, camera_y)
    
    def update_camera(self, heightmap_left_offset: int, heightmap_top_offset: int, 
                     camera_x: float, camera_y: float) -> None:
        """Update screen position when camera moves without changing world position
        
        Args:
            heightmap_left_offset: Heightmap left offset
            heightmap_top_offset: Heightmap top offset
            camera_x: Camera X position
            camera_y: Camera Y position
        """
        self._update_screen_pos(heightmap_left_offset, heightmap_top_offset, camera_x, camera_y)
    
    def _update_screen_pos(self, heightmap_left_offset: int, heightmap_top_offset: int, 
                          camera_x: float, camera_y: float) -> None:
        """Update screen position based on world position and camera (private)"""
        # Cache the parameters for potential future use
        self._heightmap_left_offset = heightmap_left_offset
        self._heightmap_top_offset = heightmap_top_offset
        self._camera_x = camera_x
        self._camera_y = camera_y
        
        offset_x: float = (heightmap_left_offset - 12 + 4) * 16
        offset_y: float = (heightmap_top_offset - 11 + 4) * 16
        iso_x: float
        iso_y: float
        iso_x, iso_y = cartesian_to_iso(self._world_pos.x - offset_x, self._world_pos.y - offset_y)
        self._screen_pos.x = iso_x - 16 - camera_x
        self._screen_pos.y = iso_y - self._world_pos.z + 12 - camera_y 
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the hero on the surface"""
        surface.blit(self.image, self._screen_pos)