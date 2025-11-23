class Warp:
    """Represents a warp zone that transitions between rooms"""
    
    def __init__(self, warp_data):
        self.room1 = warp_data['room1']
        self.room2 = warp_data['room2']
        self.x = warp_data['x']
        self.y = warp_data['y']
        self.x2 = warp_data['x2']
        self.y2 = warp_data['y2']
        self.width = warp_data['width']
        self.height = warp_data['height']
        self.warp_type = warp_data['type']
    
    def check_collision(self, hero_x, hero_y, hero_width, hero_height):
        """Check if hero collides with this warp zone"""
        return (hero_x < self.x + self.width and
                hero_x + hero_width > self.x and
                hero_y < self.y + self.height and
                hero_y + hero_height > self.y)
    
    def get_target_room(self, current_room):
        """Get the target room based on current room"""
        return self.room2 if current_room == self.room1 else self.room1
    
    def get_destination(self):
        """Get the destination coordinates"""
        return self.x2, self.y2