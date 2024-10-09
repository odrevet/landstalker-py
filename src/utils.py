def iso_to_cartesian(x, y):
    return (x - y), (x + y)

def cartesian_to_iso(x, y):
    return x - y, (x + y) // 2
    