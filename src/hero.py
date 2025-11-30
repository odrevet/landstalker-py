import pygame
from pygame.math import Vector2, Vector3
from typing import Tuple, List
from utils import cartesian_to_iso
from boundingbox import BoundingBox, MARGIN
from entity import Entity


class Hero(pygame.sprite.Sprite):
    def __init__(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        super().__init__()
        # Try to load image, create placeholder if it doesn't exist
        try:
            full_image = pygame.image.load('data/gfx/SpriteGfx000Anim001.png').convert_alpha()
            self.image: pygame.Surface = full_image
        except (pygame.error, FileNotFoundError):
            # Create a simple placeholder surface if image doesn't exist
            self.image: pygame.Surface = pygame.Surface((32, 56), pygame.SRCALPHA)
            self.image.fill((255, 0, 255, 128))  # Semi-transparent magenta placeholder
        
        self._world_pos: Vector3 = Vector3(x, y, z)
        self._screen_pos: Vector2 = Vector2()
        self.HEIGHT: int = 2   # height in tiles
        self.touch_ground: bool = False
        self.is_jumping: bool = False
        self.current_jump: int = 0
        self.is_grabbing: bool = False
        self.grabbed_entity: Optional[Entity] = None

        self.is_grabbing: bool = False
        self.grabbed_entity: Optional[Entity] = None
        self.facing_direction: str = "DOWN"  # Can be: "UP", "DOWN", "LEFT", "RIGHT"

        # Bounding box for collision detection
        self.bbox: BoundingBox = BoundingBox(self._world_pos, self.HEIGHT)
        
        # Cache for update_screen_pos parameters
        self._heightmap_left_offset: int = 0
        self._heightmap_top_offset: int = 0
        self._camera_x: float = 0
        self._camera_y: float = 0
    
    def get_world_pos(self) -> Vector3:
        """Get the hero's world position"""
        return self._world_pos
    
    def get_bounding_box(self, tile_h: int) -> Tuple[float, float, float, float]:
        """Get hero's bounding box in world coordinates with margin applied
        
        Args:
            tile_h: Tile height in pixels
            
        Returns:
            Tuple of (x, y, width, height) in world coordinates
        """
        x = self._world_pos.x + MARGIN
        y = self._world_pos.y + MARGIN
        width = tile_h - (MARGIN * 2)
        height = tile_h - (MARGIN * 2)
        return (x, y, width, height)
    
    def get_bbox_corners_world(self, tile_h: int) -> Tuple[Tuple[float, float], ...]:
        """Get the four corners of the hero's bounding box in world coordinates
        
        Args:
            tile_h: Tile height in pixels
            
        Returns:
            Tuple of 4 corner positions: (left, bottom, right, top)
            Each corner is (x, y) in world coordinates
        """
        x, y, width, height = self.get_bounding_box(tile_h)
        
        left = (x, y + height)
        bottom = (x + width, y + height)
        right = (x + width, y)
        top = (x, y)
        
        return (left, bottom, right, top)
    
    def get_bbox_corners_iso(self, tile_h: int, left_offset: int, top_offset: int, 
                              camera_x: float, camera_y: float) -> List[Tuple[float, float]]:
        """Get the four corners of the hero's bounding box in isometric screen coordinates
        
        This is useful for debug drawing.
        
        Args:
            tile_h: Tile height in pixels
            left_offset: Heightmap left offset
            top_offset: Heightmap top offset
            camera_x: Camera X position
            camera_y: Camera Y position
            
        Returns:
            List of 4 corner positions in screen space: [left, bottom, right, top]
        """
        offset_x = (left_offset - 12 + 4) * tile_h - 12
        offset_y = (top_offset - 11 + 4) * tile_h - 12
        
        corners_world = self.get_bbox_corners_world(tile_h)
        corners_iso = []
        
        for wx, wy in corners_world:
            iso_x, iso_y = cartesian_to_iso(wx - offset_x, wy - offset_y)
            corners_iso.append((iso_x - camera_x, iso_y - camera_y))
        
        return corners_iso
        
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
        HERO_HEIGHT: int = 32
        
        self._screen_pos.x = iso_x - 16 - camera_x
        self._screen_pos.y = iso_y - self._world_pos.z + 12 - camera_y + HERO_HEIGHT
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the hero on the surface"""
        surface.blit(self.image, self._screen_pos)

    def grab_entity(self, entity: Entity) -> None:
        """Start grabbing an entity
        
        Args:
            entity: The entity to grab
        """
        self.is_grabbing = True
        self.grabbed_entity = entity

    def release_entity(self) -> None:
        """Release the currently grabbed entity"""
        self.is_grabbing = False
        self.grabbed_entity = None

    def update_grabbed_entity_position(self, left_offset: int, top_offset: int, 
                                    camera_x: float, camera_y: float, tile_h: int) -> None:
        """Update the position of the grabbed entity to be above the hero
        
        Args:
            left_offset: Heightmap left offset
            top_offset: Heightmap top offset
            camera_x: Camera X position
            camera_y: Camera Y position
            tile_h: Tile height in pixels
        """
        if not self.is_grabbing or self.grabbed_entity is None:
            return
        
        # Position entity directly above hero (1 tile higher in Z)
        hero_pos = self.get_world_pos()
        entity_z = hero_pos.z + (self.HEIGHT * tile_h)
        
        self.grabbed_entity.set_world_pos(tile_h)
        self.grabbed_entity.world_pos = Vector3(hero_pos.x, hero_pos.y, entity_z)
        
        # Update entity's bounding box
        if self.grabbed_entity.bbox:
            self.grabbed_entity.bbox.update_position(self.grabbed_entity.world_pos)

    def update_facing_direction(self, keys) -> None:
        """Update hero's facing direction based on movement input
        
        Args:
            keys: Pygame key state
        """
        import pygame
        
        # Priority: most recent key press determines facing
        if keys[pygame.K_LEFT]:
            self.facing_direction = "LEFT"
        elif keys[pygame.K_RIGHT]:
            self.facing_direction = "RIGHT"
        elif keys[pygame.K_UP]:
            self.facing_direction = "UP"
        elif keys[pygame.K_DOWN]:
            self.facing_direction = "DOWN"

    def grab_entity(self, entity: Entity) -> None:
        """Start grabbing an entity
        
        Args:
            entity: The entity to grab
        """
        self.is_grabbing = True
        self.grabbed_entity = entity

    def release_entity(self) -> None:
        """Release the currently grabbed entity"""
        self.is_grabbing = False
        self.grabbed_entity = None

    def update_grabbed_entity_position(self, left_offset: int, top_offset: int, 
                                    camera_x: float, camera_y: float, tile_h: int) -> None:
        """Update the position of the grabbed entity to be above the hero
        
        Args:
            left_offset: Heightmap left offset
            top_offset: Heightmap top offset
            camera_x: Camera X position
            camera_y: Camera Y position
            tile_h: Tile height in pixels
        """
        if not self.is_grabbing or self.grabbed_entity is None:
            return
        
        from pygame.math import Vector3
        
        # Position entity directly above hero (1 tile higher in Z)
        hero_pos = self.get_world_pos()
        entity_z = hero_pos.z + (self.HEIGHT * tile_h)
        
        self.grabbed_entity.set_world_pos(tile_h)
        self.grabbed_entity.world_pos = Vector3(hero_pos.x, hero_pos.y, entity_z)
        
        # Update entity's bounding box
        if self.grabbed_entity.bbox:
            self.grabbed_entity.bbox.update_position(self.grabbed_entity.world_pos)