from player import Player
from card import Card

from typing import Tuple, List

class HumanPlayer(Player):
    
    def get_card_and_caption(self) -> Tuple[Card, str]:
        card = self.select_card_from_hand()
        caption = input("Which caption would you like to use?") 
        print(f"{self.player_name} selected card with caption {caption}")

        return card, caption

    def select_card_from_caption(self, caption: str) -> Card:
        print("\n========================\n")
        card = self.select_card_from_hand()
        return card

    def get_most_likely_card(self, cards_on_table: List[Tuple[Player, Card]], caption:str) -> Player:
        print("\n========================\n")
        print("Select the most likely card on table:")
        for _, card in cards_on_table:
            print(f"{card}")

        image_number = int(input("Insert number: "))
        valid = False
        player_to_vote = None
        while not valid:
            for player, card in cards_on_table:
                if card.image_number == image_number:
                    valid = True
                    player_to_vote = player
            if not valid:
                print("You have to insert a valid card on table!")
                image_number = int(input("Insert number: "))

        return player_to_vote

        
    def select_card_from_hand(self) -> Card:
        print("You have the following cards in your hand:")
        print(self.cards_in_hand)

        valid_card = False
        while not valid_card:
            selected_card = int(input("Which card would you like to play?\n"))
            valid_card = self.get_card_from_index(selected_card)
            if not valid_card:
                print("You have to select a card in your hand!")

        self.cards_in_hand.remove(valid_card)

        return valid_card
        
    def get_card_from_index(self, image_number: int) -> Card:
        output_card = None
        for card in self.cards_in_hand:
            if card.image_number == image_number:
                output_card = card

        return output_card

