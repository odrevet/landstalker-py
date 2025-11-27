from typing import Dict, Tuple, Any

class Warp:
    """Represents a warp zone that transitions between rooms"""
    
    def __init__(self, warp_data: Dict[str, Any]) -> None:
        self.room1: int = warp_data['room1']
        self.room2: int = warp_data['room2']
        # Warp data contains tile indices
        self.x: int = warp_data['x']
        self.y: int = warp_data['y']
        self.x2: int = warp_data['x2']
        self.y2: int = warp_data['y2']
        self.width: int = warp_data['width']
        self.height: int = warp_data['height']
        self.warp_type: str = warp_data['type']
    
    def check_collision(
        self, 
        hero_x: float, 
        hero_y: float, 
        hero_width: float, 
        hero_height: float, 
        tile_h: int, 
        current_room: int, 
        heightmap: Any
    ) -> bool:
        """Check if hero collides with this warp zone
        
        Args:
            hero_x, hero_y: Hero position in pixels (world coordinates)
            hero_width, hero_height: Hero size in pixels (not used for point collision)
            tile_h: Tile height in pixels
            current_room: Current room number
            heightmap: Heightmap object for offset calculations
        """
        # Get the correct warp tile coordinates based on current room
        if self.room1 == current_room:
            warp_tile_x = self.x
            warp_tile_y = self.y
        else:
            warp_tile_x = self.x2
            warp_tile_y = self.y2
        
        # Convert hero world position to tile coordinates
        hero_tile_x = hero_x // tile_h
        hero_tile_y = hero_y // tile_h
        
        # Apply the 12-tile offset to align warp coordinates with heightmap coordinates
        # Warp uses Tiled coordinates, heightmap has a 12-tile offset
        adjusted_warp_tile_x = warp_tile_x - 12
        adjusted_warp_tile_y = warp_tile_y - 12
        
        # Point-in-rectangle collision: check if hero tile is within warp bounds
        collision = (adjusted_warp_tile_x <= hero_tile_x < adjusted_warp_tile_x + self.width and
                    adjusted_warp_tile_y <= hero_tile_y < adjusted_warp_tile_y + self.height)
        
        return collision
    
    def get_destination(
        self, 
        current_room: int, 
        heightmap: Any
    ) -> Tuple[int, int]:
        """Get the destination coordinates in world pixels
        
        Args:
            current_room: Current room number
            
        Returns:
            Tuple of (x, y) in tile coordinates
        """
        if current_room == self.room1:
            # Going from room1 to room2, use x2, y2
            dest_tile_x = self.x2
            dest_tile_y = self.y2
        else:
            # Going from room2 to room1, use x, y
            dest_tile_x = self.x
            dest_tile_y = self.y
        
        adjusted_tile_x = dest_tile_x - 12
        adjusted_tile_y = dest_tile_y - 12
        
        return adjusted_tile_x, adjusted_tile_y
    
    def get_target_room(self, current_room: int) -> int:
        """Get the target room based on current room"""
        return self.room2 if current_room == self.room1 else self.room1