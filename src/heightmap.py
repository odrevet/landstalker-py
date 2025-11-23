class HeightmapCell:
    def __init__(self, height, walkable):
        self.height = height
        self.walkable = walkable
    
    def is_walkable(self):
        return self.walkable < 4


class Heightmap:
    def __init__(self):
        self.left_offset = 0
        self.top_offset = 0
        self.width = 0
        self.height = 0
        self.cells = []
    
    def load_from_tilemap(self, tilemap):
        """Load heightmap from a Tiledmap object's properties"""
        self.left_offset = tilemap.hmleft
        self.top_offset = tilemap.hmtop
        self.width = tilemap.hmwidth
        self.height = tilemap.hmheight
        
        # Parse the heightmap string
        heightmap_str = tilemap.heightmap
        
        # Split by newlines and commas to get individual cell values
        rows = heightmap_str.strip().split('\n')
        
        self.cells = []
        for row_str in rows:
            # Remove any trailing commas and whitespace
            row_str = row_str.strip().rstrip(',')
            
            # Split by comma to get individual hex values
            values = [v.strip() for v in row_str.split(',') if v.strip()]
            
            row_cells = []
            for value in values:
                # Parse hex value (e.g., "0x0200")
                hex_value = int(value, 16)
                
                # Extract walkable (first nibble) and height (remaining nibbles)
                # Format: 0xWHHH where W=walkable, HHH=height
                walkable = (hex_value >> 12) & 0xF
                height = hex_value & 0xFFF
                
                row_cells.append(HeightmapCell(height=height, walkable=walkable))
            
            if row_cells:  # Only add non-empty rows
                self.cells.append(row_cells)
    
    def get_width(self):
        return len(self.cells[0]) if self.cells else 0
    
    def get_height(self):
        return len(self.cells)
    
    def get_cell(self, x, y):
        if 0 <= y < len(self.cells) and 0 <= x < len(self.cells[y]):
            return self.cells[y][x]
        return None