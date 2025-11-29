from typing import Dict, Any, Optional, Tuple, List
from pygame.math import Vector3
from boundingbox import BoundingBox


class Entity:
    """Represents a game entity (NPC, chest, crate, etc.)"""
    
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
        self.x: float = data.get('X', 0.0) // 2
        self.y: float = data.get('Y', 0.0) // 2
        self.z: float = data.get('Z', 0.0) // 2
        
        # World position (will be calculated based on tile size)
        self.world_pos: Optional[Vector3] = None
        
        # Height in tiles (entities are 1 tile tall)
        self.HEIGHT: int = 1
        
        # Bounding box for collision detection (initialized after world_pos is set)
        self.bbox: Optional[BoundingBox] = None
        
        # Visual properties
        self.palette: int = data.get('Palette', 0)
        self.orientation: str = data.get('Orientation', 'NE')
        
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
    
    def get_foot_height(self, tile_h: int) -> float:
        """Get the height of the entity's feet (bottom of bounding box) in world Z
        
        Args:
            tile_h: Tile height in pixels
            
        Returns:
            Z coordinate of entity's feet
        """
        if self.bbox is None:
            raise RuntimeError("Bounding box not initialized. Call set_world_pos() first.")
        return self.bbox.get_foot_height(tile_h)
    
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