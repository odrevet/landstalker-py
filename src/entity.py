from typing import Dict, Any, Optional
from pygame.math import Vector3


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
        self.x: float = data.get('X', 0.0)
        self.y: float = data.get('Y', 0.0)
        self.z: float = data.get('Z', 0.0)
        
        # World position (will be calculated based on tile size)
        self.world_pos: Optional[Vector3] = None
        
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