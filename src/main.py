import sys
import argparse

from game import Game

def main() -> None:
    # Initialize argument parser
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="LandStalker")
    parser.add_argument('-r', '--room', type=int, default=1, help='Room number')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-x', type=int, default=0, help='Hero starting X position')
    parser.add_argument('-y', type=int, default=0, help='Hero starting Y position')
    parser.add_argument('-z', type=int, default=0, help='Hero starting Z position')
    parser.add_argument('-f', '--fullscreen', action='store_true', help='Starts fullscreen')
    
    args: argparse.Namespace = parser.parse_args()
    
    # Create and run game
    game: Game = Game(args)
    game.run()


if __name__ == "__main__":
    main()
