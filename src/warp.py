class Warp:
    """Represents a warp zone that transitions between rooms"""
    
    def __init__(self, warp_data):
        self.room1 = warp_data['room1']
        self.room2 = warp_data['room2']
        # Warp data contains tile indices
        self.x = warp_data['x']
        self.y = warp_data['y']
        self.x2 = warp_data['x2']
        self.y2 = warp_data['y2']
        self.width = warp_data['width']
        self.height = warp_data['height']
        self.warp_type = warp_data['type']
    
    def check_collision(self, hero_x, hero_y, hero_width, hero_height, tile_h, current_room, heightmap):
        """Check if hero collides with this warp zone
        
        Args:
            hero_x, hero_y: Hero position in pixels (world coordinates)
            hero_width, hero_height: Hero size in pixels
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
        
        # Apply the same offset transformation as the visual debug
        off_x = heightmap.left_offset * tile_h
        off_y = heightmap.top_offset * tile_h
        
        # Convert warp tiles to world coordinates (same as visual)
        warp_x = warp_tile_x * tile_h
        warp_y = warp_tile_y * tile_h
        warp_width = self.width * tile_h
        warp_height = self.height * tile_h
        
        # AABB collision detection in world coordinates
        collision = (hero_x < warp_x + warp_width and
                     hero_x + hero_width > warp_x and
                     hero_y < warp_y + warp_height and
                     hero_y + hero_height > warp_y)
        
        # Debug print for all warps
        #status = "COLLISION!" if collision else "no collision"
        #print(f"[WARP CHECK {status}] Room {self.room1}→{self.room2} (current: {current_room})")
        #print(f"  Hero: pos=({hero_x:.1f}, {hero_y:.1f}) size=({hero_width}, {hero_height})")
        #print(f"  Warp tile: ({warp_tile_x}, {warp_tile_y}) offset: ({off_x}, {off_y})")
        #print(f"  Warp world: pos=({warp_x:.1f}, {warp_y:.1f}) size=({warp_width}, {warp_height})")
        #print(f"  Hero bounds: [{hero_x:.1f} to {hero_x + hero_width:.1f}, {hero_y:.1f} to {hero_y + hero_height:.1f}]")
        #print(f"  Warp bounds: [{warp_x:.1f} to {warp_x + warp_width:.1f}, {warp_y:.1f} to {warp_y + warp_height:.1f}]")
        #print()
        
        return collision
    
    def get_target_room(self, current_room):
        """Get the target room based on current room"""
        return self.room2 if current_room == self.room1 else self.room1
    
    def get_destination(self, tile_h, current_room):
        """Get the destination coordinates in world pixels
        
        Args:
            tile_h: Tile height in pixels
            current_room: Current room number
            
        Returns:
            Tuple of (x, y) in pixel coordinates
        """
        if current_room == self.room1:
            # Going from room1 to room2, use x2, y2
            return self.x2 * tile_h, self.y2 * tile_h
        else:
            # Going from room2 to room1, use x, y
            return self.x * tile_h, self.y * tile_h