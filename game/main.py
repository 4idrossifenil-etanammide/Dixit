from game import Game

import argparse
from argparse import Namespace

def argument_parsing() -> Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("-np", "--n_players", type=int, default=5, help="Specify the number of players")
    parser.add_argument("-p", "--play", action="store_true", help="Let the player play against the bots")
    parser.add_argument("--gpt_players", type=int, default = 0, help = "Specify number of GPT players")
    parser.add_argument("--points_to_win", type=int, default = 30, help="Specify the number of points to win")
    parser.add_argument("--print_cards", action = "store_true", help="Print the card in the hands of the players for each round")

    return parser.parse_args()

if __name__ == "__main__":

    args = argument_parsing()

    game = Game(args.n_players, args.gpt_players, "../cards/odissey_cards", args.play, args.points_to_win, args.print_cards)
    
    game.simulate()
