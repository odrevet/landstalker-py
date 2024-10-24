import csv

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
        self.cells = []

    def load(self, map_name):
        map_filename = f"data/heightmaps/{map_name}_heightmap.csv"

        with open(map_filename, mode="r") as file:
            csv_reader = csv.reader(file)
            
            header = next(csv_reader)
            self.left_offset, self.top_offset = int(header[0], 16), int(header[1], 16)

            for row in csv_reader:
                self.cells.append([HeightmapCell(walkable=int(value[0], 16),height=int(value[1], 16)) for value in row])

    def get_width(self):
        return len(self.cells[0])

    def get_height(self):
        return len(self.cells)

    def get_cell(self, x, y):
        return self.cells[y][x]