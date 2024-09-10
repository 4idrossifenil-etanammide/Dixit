import os
from PIL import Image
import random
from typing import Dict, List
import sys

from card import Card
from human_player import HumanPlayer
from bot import Bot
from player import Player
from gpt_bot import GPT_bot

from transformers import BlipProcessor, BlipForConditionalGeneration, CLIPProcessor, CLIPModel
import torch

class Game():

    def __init__(self, n_players: int, gpt_players: int, path_to_images: str, playable: bool, points_to_win: int, print_cards: bool, path_to_blip_weights: str = "../weights/rephrased_blip(2nd)/epoch50.pt", path_to_clip_weights: str = "../weights/rephrased_coco_clip(2nd)/epoch13.pt"):
        self.playable = playable
        self.n_players = n_players
        
        self.print_cards = print_cards
        self.n_bots = n_players
        
        self.played_cards = list()
        self.deck = list()
        for image_name in os.listdir(path_to_images):
            image_number = int(image_name.split(".")[0])
            image = Image.open(os.path.join(path_to_images, image_name)).convert("RGB")
            image = image.resize((224,224))
            card = Card(image_number, image)
            self.deck.append(card)

        self.players = []
        if self.playable:
            self.n_bots -= 1
            human_player = HumanPlayer("Human Player", points_to_win) 
            self.deck = human_player.draw_initial_hand(self.deck)
            self.players.append(human_player)

        if gpt_players != 0:
            self.n_bots -= gpt_players
            if self.n_bots <= 0:
                print("Too many GPT players")
                sys.exit()
            
        api_key = " "
        for k in range(gpt_players):
            gpt = GPT_bot(f"GPT Bot {k+1}", points_to_win, api_key)
            self.deck = gpt.draw_initial_hand(self.deck)
            self.players.append(gpt)

        device = "cuda" if torch.cuda.is_available() else "cpu"

        print("Loading models...")

        blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16").to(device)
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")

        blip_model.load_state_dict(torch.load(path_to_blip_weights))
        clip_model.load_state_dict(torch.load(path_to_clip_weights))

        print("Models loaded successfully!")

        for k in range(self.n_bots):
            p = Bot(f"Bot {k+1}", points_to_win, blip_model, blip_processor, clip_model, clip_processor)
            self.deck = p.draw_initial_hand(self.deck)
            self.players.append(p)

        blip_model.eval()
        clip_model.eval()

        self.first_to_start = random.randint(0, n_players-1)

    def simulate(self) -> None:
        players_winning_conditions = {p:p.check_winning_condition() for p in self.players}
        while not any(players_winning_conditions.values()):
            if self.print_cards:
                print("PLAYERS CARDS:")
                for p in self.players:
                    print(f"{p} has the following cards: {p.cards_in_hand}")
                print()
            self.do_one_round()
            players_winning_conditions = {p:p.check_winning_condition() for p in self.players}
            points_dict = {p:p.points for p in self.players}
            print("\n" + "-"*15 + "POINTS" + "-"*15 + "\n")
            for p, points in points_dict.items():
                print(f"{p}: {points}")
            print("\n" + "="*35 + "\n")

        final_points = {p:p.points for p in self.players}
        
        max_score = max(final_points.values())
        winners = [player for player, score in final_points.items() if score == max_score]

        for player in winners:
            print(f"{player} has won!")

    
    def do_one_round(self) -> None:
        current_player = self.first_to_start
        print("\n" + "-"*10 + "NARRATOR PHASE" + "-"*10 + "\n")
        selected_card, caption = self.players[current_player].get_card_and_caption()
        
        other_players = [player for player_index, player in enumerate(self.players) if player_index != current_player]
        print("\n" + "-"*10 + "SELECTION PHASE" + "-"*10 + "\n")
        cards_on_table = [(player, player.select_card_from_caption(caption)) for player in other_players]
        cards_on_table.append((self.players[current_player], selected_card))

        print("\n" + "-"*10 + "VOTING PHASE" + "-"*10 + "\n")
        votes = {p:[] for p in self.players} #Key: player Value: players who voted for him
        for player in other_players:
            others_card_on_table = [(player_who_played_card,card) for player_who_played_card,card in cards_on_table if player != player_who_played_card]
            player_vote = player.get_most_likely_card(others_card_on_table, caption)
            votes[player_vote].append(player)

        print("\n" + "-"*15 + "VOTES" + "-"*15 + "\n")
        for player, players_who_voted in votes.items():
            players_who_voted = ", ".join([str(p) for p in players_who_voted]) if len(players_who_voted) != 0 else "no one"
            played_card = None
            for p, card in cards_on_table:
                if p == player:
                    played_card = card
                    break
            print(f"{player} with card {played_card} has been voted by {players_who_voted}")

        self.compute_scores(votes, current_player, other_players)

        for _, card in cards_on_table:
            self.played_cards.append(card)
        
        # If there are less cards in the deck than players, shuffle and reuse the already played ones
        if len(self.deck) < self.n_players:

            # If there are still some cards in the deck (not enough for all the players), add them to the already played ones
            for card in self.deck:
                self.played_cards.append(card)

            #Shuffle and reuse the already played cards
            random.shuffle(self.played_cards)
            self.deck = self.played_cards.copy() # Shallow copy of already played cards

        # Each player takes a card
        for player in self.players:
            self.deck = player.draw_card(self.deck)

        #Compute next player. If the current is the last one, we skip to the first one
        next_player = (current_player + 1) % self.n_players
        self.first_to_start = next_player


    def compute_scores(self, votes: Dict[Player, List[Player]], current_player: int, other_players: List[Player]) -> None:
        narrator = self.players[current_player]

        # If everyone or no one has voted for the narrator, everyone else get two points
        if (len(votes[narrator]) == 0) or (len(votes[narrator]) == len(other_players)):
            for player in other_players:
                player.add_points(2)
            return

        # For each vote given to a player that's not the narrator, said player gets a point
        for player in other_players:
            player.add_points(len(votes[player]))

        # The narrator gets 3 points if someone voted for him (Given the intiial check, this line is exectuted if and only if someone voted for him but not everyone)
        narrator.add_points(3)
        
        # Everyone that has voted for the narrator takes 3 points
        for player in votes[narrator]:
            player.add_points(3)

