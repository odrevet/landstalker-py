from typing import Optional, Tuple, List
from pygame.math import Vector3
from entity import Entity
from hero import Hero


# MARGIN constant for consistency with boundingbox.py
MARGIN: int = 2


def check_entity_collision_3d(moving_entity_bbox: Tuple[float, float, float, float],
                              moving_entity_z: float,
                              moving_entity_height: float,
                              target_entity: Entity,
                              tile_h: int) -> bool:
    """Check if a moving entity's 3D bounding box collides with a target entity
    
    Args:
        moving_entity_bbox: Bounding box of moving entity (x, y, width, height) in XY plane
        moving_entity_z: Z position (bottom) of moving entity
        moving_entity_height: Height of moving entity in world units
        target_entity: Entity to check collision against
        tile_h: Tile height in pixels
        
    Returns:
        True if collision detected, False otherwise
    """
    if not target_entity.solid or not target_entity.visible:
        return False
    
    # Get target entity bounding box and Z position
    target_bbox = target_entity.get_bounding_box(tile_h)
    target_z = target_entity.world_pos.z
    target_height = target_entity.HEIGHT * tile_h
    
    # Check XY plane collision (AABB)
    me_x, me_y, me_w, me_h = moving_entity_bbox
    te_x, te_y, te_w, te_h = target_bbox
    
    xy_collision = (me_x < te_x + te_w and
                    me_x + me_w > te_x and
                    me_y < te_y + te_h and
                    me_y + me_h > te_y)
    
    if not xy_collision:
        return False
    
    # Check Z axis collision
    # Moving entity occupies: moving_entity_z to (moving_entity_z + moving_entity_height)
    # Target entity occupies: target_z to (target_z + target_height)
    z_collision = (moving_entity_z < target_z + target_height and
                   moving_entity_z + moving_entity_height > target_z)
    
    return z_collision


def get_entity_top_at_position(entities: List[Entity],
                               x: float,
                               y: float,
                               width: float,
                               height: float,
                               below_z: float,
                               tile_h: int) -> Optional[float]:
    """Get the highest entity top surface at the given XY position that's below the given Z
    
    This is used for gravity - finding what entity surface the hero should land on.
    
    Args:
        entities: List of entities to check
        x: X position of bounding box
        y: Y position of bounding box
        width: Width of bounding box
        height: Height of bounding box
        below_z: Only consider entities whose top is at or below this Z
        tile_h: Tile height in pixels
        
    Returns:
        Z coordinate of highest entity top surface, or None if no entity found
    """
    highest_top: Optional[float] = None
    
    for entity in entities:
        if not entity.solid or not entity.visible:
            continue
        
        # Get entity bounds
        e_bbox = entity.get_bounding_box(tile_h)
        e_x, e_y, e_w, e_h = e_bbox
        e_z = entity.world_pos.z
        e_top = e_z + entity.HEIGHT * tile_h
        
        # Check if entity is below the threshold
        if e_top > below_z:
            continue
        
        # Check XY overlap
        if (x < e_x + e_w and
            x + width > e_x and
            y < e_y + e_h and
            y + height > e_y):
            
            # This entity overlaps in XY and is below threshold
            if highest_top is None or e_top > highest_top:
                highest_top = e_top
    
    return highest_top


def resolve_entity_collision(hero: Hero,
                            entities: List[Entity],
                            new_x: float,
                            new_y: float,
                            tile_h: int,
                            left_offset: int,
                            top_offset: int,
                            camera_x: float,
                            camera_y: float) -> Tuple[float, float]:
    """Resolve XY collision between hero and entities by placing hero at edge of collision
    
    Only resolves horizontal (XY) collisions. Does not handle Z/gravity.
    
    Args:
        hero: The hero object
        entities: List of entities to check collision against
        new_x: Proposed new X position for hero
        new_y: Proposed new Y position for hero
        tile_h: Tile height in pixels
        left_offset: Heightmap left offset
        top_offset: Heightmap top offset
        camera_x: Camera X position
        camera_y: Camera Y position
        
    Returns:
        Tuple of (resolved_x, resolved_y) - adjusted position if collision detected
    """
    hero_pos = hero.get_world_pos()
    hero_z = hero_pos.z
    hero_height = hero.HEIGHT * tile_h
    
    # Create temporary position to test collision
    temp_pos = Vector3(new_x, new_y, hero_pos.z)
    hero.world_pos = temp_pos
    proposed_bbox = hero.get_bounding_box(tile_h)
    
    # Restore original position
    hero.world_pos = hero_pos
    
    # Check collision with each entity
    for entity in entities:
        if check_entity_collision_3d(proposed_bbox, hero_z, hero_height, entity, tile_h):
            # Collision detected - check if hero is above the entity
            entity_top = entity.world_pos.z + entity.HEIGHT * tile_h
            
            # If hero's feet are above the entity's top, allow horizontal movement
            # (hero is jumping/walking over the entity)
            if hero_z >= entity_top:
                continue
            
            # Hero is at same level or intersecting - resolve XY collision
            entity_bbox = entity.get_bounding_box(tile_h)
            e_x, e_y, e_w, e_h = entity_bbox
            h_x, h_y, h_w, h_h = proposed_bbox
            
            # Calculate center positions
            hero_center_x = h_x + h_w / 2
            hero_center_y = h_y + h_h / 2
            entity_center_x = e_x + e_w / 2
            entity_center_y = e_y + e_h / 2
            
            # Calculate overlap on each axis
            dx = hero_center_x - entity_center_x
            dy = hero_center_y - entity_center_y
            
            # Calculate penetration depth on each axis
            overlap_x = (h_w + e_w) / 2 - abs(dx)
            overlap_y = (h_h + e_h) / 2 - abs(dy)
            
            # Resolve collision on axis with smallest overlap
            if overlap_x < overlap_y:
                # Resolve horizontally
                if dx > 0:
                    # Hero is to the right of entity
                    new_x = e_x + e_w + (new_x - h_x)
                else:
                    # Hero is to the left of entity
                    new_x = e_x - h_w + (new_x - h_x)
            else:
                # Resolve vertically
                if dy > 0:
                    # Hero is below entity
                    new_y = e_y + e_h + (new_y - h_y)
                else:
                    # Hero is above entity
                    new_y = e_y - h_h + (new_y - h_y)
            
            # Re-check with adjusted position
            temp_pos = Vector3(new_x, new_y, hero_pos.z)
            hero.world_pos = temp_pos
            proposed_bbox = hero.get_bounding_box(tile_h)
            hero.world_pos = hero_pos
    
    return (new_x, new_y)


def can_move_to_position(hero: Hero,
                        entities: List[Entity],
                        new_x: float,
                        new_y: float,
                        tile_h: int) -> bool:
    """Check if hero can move to a position without colliding with entities
    
    Args:
        hero: The hero object
        entities: List of entities to check collision against
        new_x: Proposed new X position for hero
        new_y: Proposed new Y position for hero
        tile_h: Tile height in pixels
        
    Returns:
        True if position is free, False if blocked by entity
    """
    hero_pos = hero.get_world_pos()
    hero_z = hero_pos.z
    hero_height = hero.HEIGHT * tile_h
    
    # Create temporary position to test collision
    temp_pos = Vector3(new_x, new_y, hero_pos.z)
    hero.world_pos = temp_pos
    proposed_bbox = hero.get_bounding_box(tile_h)
    
    # Restore original position
    hero.world_pos = hero_pos
    
    # Check collision with each solid entity
    for entity in entities:
        if check_entity_collision_3d(proposed_bbox, hero_z, hero_height, entity, tile_h):
            # Check if hero is above the entity
            entity_top = entity.world_pos.z + entity.HEIGHT * tile_h
            if hero_z >= entity_top:
                continue  # Hero is above, can move over it
            
            return False  # Blocked by entity
    
    return True