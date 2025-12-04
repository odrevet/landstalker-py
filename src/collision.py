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


def get_touching_entities(hero: Hero,
                          entities: List[Entity],
                          tile_h: int) -> List[Entity]:
    """Get all entities currently touching the hero in 3D space
    
    This checks collision at the hero's current position without any movement.
    Useful for detecting enemy attacks, trigger zones, etc.
    
    Args:
        hero: The hero object
        entities: List of entities to check collision against
        tile_h: Tile height in pixels
        
    Returns:
        List of entities currently in contact with the hero
    """
    hero_pos = hero.get_world_pos()
    hero_z = hero_pos.z
    hero_height = hero.HEIGHT * tile_h
    hero_bbox = hero.get_bounding_box(tile_h)
    
    touching_entities: List[Entity] = []
    
    for entity in entities:
        if entity is hero.grabbed_entity:
            # Skip grabbed entity (it's supposed to be touching)
            continue
            
        if check_entity_collision_3d(hero_bbox, hero_z, hero_height, entity, tile_h):
            # Check if hero is above the entity (standing on top)
            entity_top = entity.world_pos.z + entity.HEIGHT * tile_h
            
            # If hero's feet are significantly above the entity's top, 
            # they're not really "touching" for interaction purposes
            # (Add small tolerance for floating point precision)
            if hero_z > entity_top + 1.0:
                continue
            
            touching_entities.append(entity)
    
    return touching_entities


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
                            camera_y: float) -> Tuple[float, float, List[Entity]]:
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
        Tuple of (resolved_x, resolved_y, touched_entities)
        - resolved_x, resolved_y: adjusted position if collision detected
        - touched_entities: list of entities that were collided with
    """
    hero_pos = hero.get_world_pos()
    hero_z = hero_pos.z
    hero_height = hero.HEIGHT * tile_h
    
    touched_entities: List[Entity] = []
    
    # Create temporary position to test collision
    temp_pos = Vector3(new_x, new_y, hero_pos.z)
    hero.world_pos = temp_pos
    proposed_bbox = hero.get_bounding_box(tile_h)
    
    # Restore original position
    hero.world_pos = hero_pos
    
    # Check collision with each entity
    for entity in entities:
        if entity is hero.grabbed_entity:
            # Skip grabbed entity
            continue
            
        if check_entity_collision_3d(proposed_bbox, hero_z, hero_height, entity, tile_h):
            # Collision detected
            touched_entities.append(entity)
            
            # Check if hero is above the entity
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
    
    return (new_x, new_y, touched_entities)


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
        if entity is hero.grabbed_entity:
            continue
            
        if check_entity_collision_3d(proposed_bbox, hero_z, hero_height, entity, tile_h):
            # Check if hero is above the entity
            entity_top = entity.world_pos.z + entity.HEIGHT * tile_h
            if hero_z >= entity_top:
                continue  # Hero is above, can move over it
            
            return False  # Blocked by entity
    
    return True


def get_entity_in_front_of_hero(hero: Hero,
                                entities: List[Entity],
                                tile_h: int,
                                max_distance: float = None) -> Optional[Entity]:
    """Get the entity directly in front of the hero within pickup range
    
    Args:
        hero: The hero object
        entities: List of entities to check
        tile_h: Tile height in pixels
        max_distance: Maximum distance to check (default: half a tile)
        
    Returns:
        Entity in front of hero, or None if no entity found
    """
    if max_distance is None:
        max_distance = tile_h
    
    hero_pos = hero.get_world_pos()
    hero_bbox = hero.get_bounding_box(tile_h)
    hero_x, hero_y, hero_w, hero_h = hero_bbox
    hero_center_x = hero_x + hero_w / 2
    hero_center_y = hero_y + hero_h / 2
    
    print(f"\n=== PICKUP DEBUG ===")
    print(f"Hero center: ({hero_center_x:.1f}, {hero_center_y:.1f}, {hero_pos.z:.1f})")
    print(f"Max pickup distance: {max_distance:.1f}")
    print(f"Total entities: {len(entities)}")
    
    closest_entity: Optional[Entity] = None
    closest_distance: float = float('inf')
    
    for entity in entities:
        if entity is hero.grabbed_entity:
            continue
            
        print(f"\nChecking entity: {entity.name} (class: {entity.entity_class})")
        print(f"  - no_pickup: {entity.no_pickup}")
        print(f"  - visible: {entity.visible}")
        print(f"  - solid: {entity.solid}")
        
        # Skip entities that can't be picked up
        if entity.no_pickup:
            print(f"  -> SKIPPED (no_pickup is True)")
            continue
        
        if not entity.visible:
            print(f"  -> SKIPPED (not visible)")
            continue
            
        if not entity.solid:
            print(f"  -> SKIPPED (not solid)")
            continue
        
        # Get entity position
        entity_bbox = entity.get_bounding_box(tile_h)
        e_x, e_y, e_w, e_h = entity_bbox
        e_center_x = e_x + e_w / 2
        e_center_y = e_y + e_h / 2
        
        print(f"  - Entity center: ({e_center_x:.1f}, {e_center_y:.1f}, {entity.world_pos.z:.1f})")
        
        # Check if entity is at similar Z level (within 1 tile)
        entity_z = entity.world_pos.z
        z_diff = abs(hero_pos.z - entity_z)
        print(f"  - Z difference: {z_diff:.1f} (max: {tile_h})")
        
        if z_diff > tile_h:
            print(f"  -> SKIPPED (Z too different)")
            continue
        
        # Calculate distance from hero center to entity center
        dx = e_center_x - hero_center_x
        dy = e_center_y - hero_center_y
        distance = (dx * dx + dy * dy) ** 0.5
        
        print(f"  - XY distance: {distance:.1f} on {max_distance}")
        
        # Check if within range
        if distance <= max_distance:
            print(f"  -> IN RANGE!")
            if distance < closest_distance:
                print(f"  -> NEW CLOSEST ENTITY")
                closest_entity = entity
                closest_distance = distance
        else:
            print(f"  -> OUT OF RANGE")
    
    if closest_entity:
        print(f"\n✓ Found entity: {closest_entity.name} at distance {closest_distance:.1f}")
    else:
        print(f"\n✗ No entity found in range")
    print("===================\n")
    
    return closest_entity


def can_place_entity_at_position(entity: Entity,
                                 x: float,
                                 y: float,
                                 z: float,
                                 entities: List[Entity],
                                 heightmap,
                                 tile_h: int) -> bool:
    """Check if an entity can be placed at the given position
    
    Args:
        entity: The entity to place
        x: X position in world coordinates
        y: Y position in world coordinates
        z: Z position in world coordinates
        entities: List of other entities to check collision against
        heightmap: The heightmap to check terrain collision
        tile_h: Tile height in pixels
        
    Returns:
        True if position is valid, False otherwise
    """
    # Check heightmap bounds and walkability
    tile_x = int(x // tile_h)
    tile_y = int(y // tile_h)
    
    if (tile_x < 0 or tile_y < 0 or
        tile_x >= heightmap.get_width() or
        tile_y >= heightmap.get_height()):
        return False
    
    cell = heightmap.get_cell(tile_x, tile_y)
    if not cell or not cell.is_walkable():
        return False
    
    # Check if Z is at ground level
    ground_z = cell.height * tile_h
    if z != ground_z:
        return False
    
    # Create temporary bounding box for the entity at new position
    temp_pos = Vector3(x, y, z)
    original_pos = entity.world_pos
    entity.world_pos = temp_pos
    
    try:
        entity_bbox = entity.get_bounding_box(tile_h)
        entity_height = entity.HEIGHT * tile_h
        
        # Check collision with other entities
        for other_entity in entities:
            if other_entity is entity:
                continue
            
            if check_entity_collision_3d(entity_bbox, z, entity_height, other_entity, tile_h):
                return False
        
        return True
    finally:
        # Restore original position
        entity.world_pos = original_pos


def get_position_in_front_of_hero(hero: Hero, tile_h: int, distance: float = None) -> Tuple[float, float]:
    """Calculate a position in front of the hero based on their facing direction
    
    For now, this returns a position 1 tile in front based on the isometric layout.
    In a full implementation, this would use the hero's facing direction.
    
    Args:
        hero: The hero object
        tile_h: Tile height in pixels
        distance: Distance in front (default: 1 tile)
        
    Returns:
        Tuple of (x, y) in world coordinates
    """
    if distance is None:
        distance = tile_h
    
    hero_pos = hero.get_world_pos()
    hero_bbox = hero.get_bounding_box(tile_h)
    hero_x, hero_y, hero_w, hero_h = hero_bbox
    hero_center_x = hero_x + hero_w / 2
    hero_center_y = hero_y + hero_h / 2
    
    # For isometric games, "in front" depends on facing direction
    # This is a simplified version - you should use hero's actual facing direction
    # For now, try positions in cardinal directions and pick the closest to center
    
    # Return position slightly offset (you can improve this with actual facing direction)
    return (hero_center_x, hero_center_y + distance)