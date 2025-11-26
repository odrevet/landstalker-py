import csv
from typing import List, Optional


class HeightmapCell:
    def __init__(self, height: int, walkable: int) -> None:
        self.height: int = height
        self.walkable: int = walkable
    
    def is_walkable(self) -> bool:
        return self.walkable < 4


class Heightmap:
    def __init__(self) -> None:
        self.left_offset: int = 0
        self.top_offset: int = 0
        self.cells: List[List[HeightmapCell]] = []
    
    def load(self, map_name: str) -> None:
        map_filename: str = f"data/heightmaps/{map_name}_heightmap.csv"
        with open(map_filename, mode="r") as file:
            csv_reader: csv.reader = csv.reader(file)
            header: List[str] = next(csv_reader)
            self.left_offset, self.top_offset = int(header[0], 16), int(header[1], 16)
            
            for row in csv_reader:
                self.cells.append([
                    HeightmapCell(
                        walkable=int(value[0], 16),
                        height=int(value[1], 16)
                    ) for value in row
                ])
    
    def get_width(self) -> int:
        return len(self.cells[0]) if self.cells else 0
    
    def get_height(self) -> int:
        return len(self.cells)
    
    def get_cell(self, x: int, y: int) -> Optional[HeightmapCell]:
        if 0 <= y < len(self.cells) and 0 <= x < len(self.cells[0]):
            return self.cells[y][x]
        return None