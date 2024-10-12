import csv

import pygame
from pytmx.util_pygame import load_pygame

from hero import Hero
from utils import cartesian_to_iso, iso_to_cartesian
from debug import draw_heightmap


class Block:
    def __init__(self, value):
        self.value = value
        print(f"{self.value} -> {bin(self.value)}")

class Blockset:
    def __init__(self):
        self.blocks = []

    def load(self, filename, page):
        with open(filename, mode="r") as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                self.blocks.append([Block(int(value, 16)) for value in row])    

