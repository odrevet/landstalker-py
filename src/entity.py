from typing import Dict, Any, Optional, Tuple, List, ClassVar
import pygame
from pygame.math import Vector2, Vector3
from boundingbox import BoundingBox
from utils import cartesian_to_iso


class Entity:
    """Represents a game entity (NPC, chest, crate, etc.)"""
    
    # Class-level sprite cache - shared across all instances
    _sprite_cache: ClassVar[Dict[str, pygame.Surface]] = {}
    
    # Sprite mapping: entity_class -> sprite filename
    _sprite_map: ClassVar[Dict[str, str]] = {
        'Crate': 'data/sprites/SpriteGfx091Anim000.png',
        'Chest': 'data/sprites/SpriteGfx036Anim000.png',
    }
    
    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize entity from TMX object data
        
        Args:
            data: Dictionary containing entity properties from TMX
        """
        # Basic identification
        self.name: str = data.get('name', 'Unknown')
        self.entity_class: str = data.get('class', 'Entity')
        self.type: int = data.get('Type', 0)
        
        # Position (in tile coordinates from TMX)
        self.x: float = data.get('X', 0.0)
        self.y: float = data.get('Y', 0.0)
        self.z: float = data.get('Z', 0.0)
        
        # World position (will be calculated based on tile size)
        self.world_pos: Optional[Vector3] = None
        self._screen_pos: Vector2 = Vector2()
        
        # Height in tiles (entities are 1 tile tall)
        self.HEIGHT: int = 1
        
        # Bounding box for collision detection (initialized after world_pos is set)
        self.bbox: Optional[BoundingBox] = None
        
        # Visual properties
        self.palette: int = data.get('Palette', 0)
        self.orientation: str = data.get('Orientation', 'NE')
        
        # Sprite/animation
        self.image: Optional[pygame.Surface] = None
        self.current_frame: int = 0
        
        # Behavior properties
        self.behaviour: int = data.get('Behaviour', 0)
        self.dialogue: int = data.get('Dialogue', 0)
        self.speed: int = data.get('Speed', 0)
        
        # Flags
        self.hostile: bool = data.get('Hostile', False)
        self.no_rotate: bool = data.get('NoRotate', False)
        self.no_pickup: bool = data.get('NoPickup', False)
        self.has_dialogue: bool = data.get('HasDialogue', False)
        self.visible: bool = data.get('Visible', True)
        self.solid: bool = data.get('Solid', True)
        self.gravity: bool = data.get('Gravity', True)
        self.friction: bool = data.get('Friction', True)
        self.reserved: bool = data.get('Reserved', False)
        
        # Tile properties (for tile copying)
        self.tile_copy: bool = data.get('TileCopy', False)
        self.tile_source: int = data.get('TileSource', 0)
        
        # Load sprite for this entity
        self._load_sprite()
    
    def _load_sprite(self) -> None:
        """Load sprite for this entity class (uses cache to avoid reloading)"""
        sprite_file = self._sprite_map.get(self.name)
        
        if sprite_file:
            # Check if already in cache
            if sprite_file not in Entity._sprite_cache:
                try:
                    loaded_sprite = pygame.image.load(sprite_file).convert_alpha()
                    Entity._sprite_cache[sprite_file] = loaded_sprite
                    print(f"Loaded sprite for {self.entity_class}: {sprite_file}")
                except (pygame.error, FileNotFoundError) as e:
                    print(f"Warning: Could not load sprite {sprite_file}: {e}")
                    # Create placeholder
                    placeholder = pygame.Surface((32, 48), pygame.SRCALPHA)
                    placeholder.fill((0, 255, 255, 128))  # Cyan placeholder
                    Entity._sprite_cache[sprite_file] = placeholder
            
            # Use cached sprite
            self.image = Entity._sprite_cache[sprite_file]
        else:
            # No sprite mapping for this entity class - create placeholder
            cache_key = f"placeholder_{self.entity_class}"
            if cache_key not in Entity._sprite_cache:
                placeholder = pygame.Surface((32, 48), pygame.SRCALPHA)
                placeholder.fill((255, 128, 0, 128))  # Orange placeholder for unknown
                Entity._sprite_cache[cache_key] = placeholder
            self.image = Entity._sprite_cache[cache_key]
    
    def set_world_pos(self, tile_h: int) -> None:
        """Calculate world position from tile coordinates
        
        Args:
            tile_h: Tile height in pixels
        """
        self.world_pos = Vector3(
            self.x * tile_h,
            self.y * tile_h,
            self.z * tile_h
        )
        # Initialize bounding box after world position is set
        self.bbox = BoundingBox(self.world_pos, self.HEIGHT)
    
    def update_screen_pos(self, heightmap_left_offset: int, heightmap_top_offset: int,
                         camera_x: float, camera_y: float, tile_h: int) -> None:
        """Update screen position based on world position and camera
        
        Args:
            heightmap_left_offset: Heightmap left offset
            heightmap_top_offset: Heightmap top offset
            camera_x: Camera X position
            camera_y: Camera Y position
            tile_h: Tile height in pixels
        """
        if self.world_pos is None:
            return
        
        offset_x: float = (heightmap_left_offset - 12 + 4) * tile_h
        offset_y: float = (heightmap_top_offset - 11 + 4) * tile_h
        
        iso_x: float
        iso_y: float
        iso_x, iso_y = cartesian_to_iso(
            self.world_pos.x - offset_x,
            self.world_pos.y - offset_y
        )
        
        ENTITY_HEIGHT: int = 32  # Adjust based on sprite
        
        self._screen_pos.x = iso_x - 16 - camera_x
        self._screen_pos.y = iso_y - self.world_pos.z + 12 - camera_y + ENTITY_HEIGHT
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the entity on the surface
        
        Args:
            surface: Pygame surface to draw on
        """
        if self.image and self.visible:
            surface.blit(self.image, self._screen_pos)
    
    def get_bounding_box(self, tile_h: int) -> Tuple[float, float, float, float]:
        """Get entity's bounding box in world coordinates with margin applied
        
        Args:
            tile_h: Tile height in pixels
            
        Returns:
            Tuple of (x, y, width, height) in world coordinates
        """
        if self.bbox is None:
            raise RuntimeError("Bounding box not initialized. Call set_world_pos() first.")
        return self.bbox.get_bounding_box(tile_h)
    
    def get_bbox_corners_world(self, tile_h: int) -> Tuple[Tuple[float, float], ...]:
        """Get the four corners of the entity's bounding box in world coordinates
        
        Args:
            tile_h: Tile height in pixels
            
        Returns:
            Tuple of 4 corner positions: (left, bottom, right, top)
            Each corner is (x, y) in world coordinates
        """
        if self.bbox is None:
            raise RuntimeError("Bounding box not initialized. Call set_world_pos() first.")
        return self.bbox.get_corners_world(tile_h)
    
    def get_bbox_corners_iso(self, tile_h: int, left_offset: int, top_offset: int, 
                              camera_x: float, camera_y: float) -> List[Tuple[float, float]]:
        """Get the four corners of the entity's bounding box in isometric screen coordinates
        
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
        if self.bbox is None:
            raise RuntimeError("Bounding box not initialized. Call set_world_pos() first.")
        return self.bbox.get_corners_iso(tile_h, left_offset, top_offset, camera_x, camera_y)
        
    def is_crate(self) -> bool:
        """Check if entity is a crate"""
        return self.entity_class == 'Crate'
    
    def is_chest(self) -> bool:
        """Check if entity is a chest"""
        return self.entity_class == 'Chest'
    
    def is_npc(self) -> bool:
        """Check if entity is an NPC"""
        return self.entity_class == 'NPC'
    
    def __repr__(self) -> str:
        return (f"Entity(name='{self.name}', class='{self.entity_class}', "
                f"pos=({self.x}, {self.y}, {self.z}), type={self.type})")