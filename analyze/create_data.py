import os
import argparse
from argparse import Namespace
from typing import List, Tuple
import pandas as pd
import re

def argument_parsing() -> Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("-src", "--src_folder", type=str, help="Specify the directory from which we want to take the data", required=True)
    parser.add_argument("-dst", "--dst_folder", type=str, help="Specify the directory to which we want to save the data", required=True)

    return parser.parse_args()

def create_directories(src_folder: str, dst_folder: str) -> List[Tuple[str, str]]:
    files = []

    for dir_path, _, filenames in os.walk(src_folder):
        
        relative_path = os.path.relpath(dir_path, src_folder)
        dest_path = os.path.join(dst_folder, relative_path)

        os.makedirs(dest_path, exist_ok=True)

        for filename in filenames:
            if filename.endswith('.txt'):
                source_file_path = os.path.join(dir_path, filename)
                destination_file_path = os.path.join(dest_path, filename)
                files.append((source_file_path, destination_file_path))

    return files

def parse_data(path_to_game: str, path_to_save: str) -> None:

    with open(path_to_game, "r") as f:
        lines = f.readlines()

    players_cards = {}
    narrations = []
    votes = []
    points = []

    round_num = 0
    i = 0
    while i < len(lines):
        line = lines[i]
            
        if "PLAYERS CARDS:" in line:
            round_num += 1
            players_cards[round_num] = {}
            i += 1
            continue
            
        if re.match(r'^[A-Za-z\s0-9]+ has the following cards:', line):
            player, cards = line.split(" has the following cards: ")
            cards = cards.strip().strip('[]').split(", ")
            players_cards[round_num][player.strip()] = cards

        elif "is giving a caption..." in line:
            player = line.split(" is giving a caption...")[0].strip()
            caption_line = lines[i + 1]
            caption = re.search(r'selected a card with caption: "(.*)"', caption_line).group(1)
            narrations.append((round_num, player, caption))
            i += 1

        elif re.match(r'^[A-Za-z\s0-9]+ with card \d+ has been voted by', line):
            details = line.split(' with card ')
            player = details[0].strip()
            card_info, votes_info = details[1].split(' has been voted by ')
            card_number = int(card_info.strip())
            voted_by = votes_info.strip()
            votes.append((round_num, player, card_number, voted_by))

        elif "POINTS" in line:
            i += 2  # Move to the next line after "POINTS"
            while i < len(lines) and re.match(r'^[A-Za-z\s0-9]+: \d+', lines[i]):
                player, score = lines[i].split(": ")
                points.append((round_num, player.strip(), int(score)))
                i += 1
            continue  

        i += 1 

    winners = ("").join(lines).split("===================================")[-1].strip()
    winners = winners.split("\n")
    winners = [line.split(" has won!")[0] for line in winners]
    players = set([x[1] for x in votes])

    win_stats = []
    for player in players:
        if player in winners:
            win_stats.append((player, 1))
        else:
            win_stats.append((player, 0))

    cards_df = pd.DataFrame([(rnd, ply, card) for rnd, ply_cards in players_cards.items() for ply, cards in ply_cards.items() for card in cards], columns=['Round', 'Player', 'Card'])
    narrations_df = pd.DataFrame(narrations, columns=['Round', 'Narrator', 'Caption'])
    votes_df = pd.DataFrame(votes, columns=['Round', 'Player', 'Card', 'Voted By'])
    points_df = pd.DataFrame(points, columns=['Round', 'Player', 'Points'])
    win_df = pd.DataFrame(win_stats, columns=['Player', 'Winner'])

    with pd.ExcelWriter(path_to_save[:-4] + ".xlsx") as writer:
        cards_df.to_excel(writer, sheet_name='Cards', index=False)
        narrations_df.to_excel(writer, sheet_name='Narrations', index=False)
        votes_df.to_excel(writer, sheet_name='Votes', index=False)
        points_df.to_excel(writer, sheet_name='Points', index=False)
        win_df.to_excel(writer, sheet_name='Winners', index=False)


if __name__ == "__main__":

    args = argument_parsing()

    src_folder = args.src_folder
    dst_folder = args.dst_folder

    files = create_directories(src_folder, dst_folder)
    
    for file in files:
        parse_data(file[0], file[1])