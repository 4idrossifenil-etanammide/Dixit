from typing import List, Tuple
import random
import torch

from transformers import BlipModel, BlipProcessor, CLIPModel, CLIPProcessor

from player import Player
from card import Card

class Bot(Player):
    
    def __init__(self, player_name: str, points_to_win: int, blip_model: BlipModel, blip_processor: BlipProcessor, clip_model: CLIPModel, clip_processor: CLIPProcessor):
        super().__init__(player_name, points_to_win)

        self.blip_model = blip_model
        self.blip_processor = blip_processor

        self.clip_model = clip_model
        self.clip_processor = clip_processor

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def get_card_and_caption(self) -> Tuple[Card, str]:
        print(f"{self.player_name} is giving a caption...")
        card_to_play = random.choice(self.cards_in_hand)
        inputs = self.blip_processor(card_to_play.image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            caption_ids = self.blip_model.generate(
                **inputs,
                max_length=50, 
                num_return_sequences=1,
                do_sample=True,
                top_k=50,      
                top_p=0.95,    
                temperature=0.7,
                repetition_penalty=1.2, 
                no_repeat_ngram_size=3 
            )

        caption = self.blip_processor.decode(caption_ids[0], skip_special_tokens=True)
        print(f"{self.player_name} selected a card with caption: \"{caption}\"")

        self.cards_in_hand.remove(card_to_play)
        return card_to_play, caption

    def select_card_from_caption(self, caption: str) -> Card:
        print(f"{self.player_name} is selecting a card...")
        inputs = self.clip_processor(text=caption, images=[card.image for card in self.cards_in_hand], return_tensors="pt", padding="max_length", truncation=True).to(self.device)

        with torch.no_grad():
            outputs = self.clip_model(**inputs)
        
        logits_per_image = outputs.logits_per_image

        probs_per_image = logits_per_image.softmax(dim=0).squeeze()
        max_score_idx = torch.argmax(probs_per_image).item()
        card = self.cards_in_hand[max_score_idx]
        self.cards_in_hand.remove(card)
        return card

    def get_most_likely_card(self, cards_on_table: List[Tuple[Player, Card]], caption: str) -> Player:
        print(f"{self.player_name} is voting...")
        inputs = self.clip_processor(text=caption, images=[player_card[1].image for player_card in cards_on_table], return_tensors="pt", padding="max_length", truncation=True).to(self.device)

        with torch.no_grad():
            outputs = self.clip_model(**inputs)
        
        logits_per_image = outputs.logits_per_image

        probs_per_image = logits_per_image.softmax(dim=0).squeeze()
        max_score_idx = torch.argmax(probs_per_image).item()
        return cards_on_table[max_score_idx][0]

