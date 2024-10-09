def iso_to_cartesian(x, y, tile_width, tile_height):
    return (x - y) * tile_width // 2, (x + y) * tile_height // 2

def cartesian_to_iso(x, y):
    return x - y, (x + y) // 2
    