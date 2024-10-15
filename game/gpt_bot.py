from player import Player
from card import Card

from typing import List, Tuple
import base64
import io
import requests
import time
import re
import sys

class GPT_bot(Player):
    def __init__(self, player_name: str, points_to_win: int, api_key: str):
        super().__init__(player_name, points_to_win)

        self.api_key = api_key

        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    def encode_image(self, image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG") 
        image_bytes = buffered.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')

    def get_card_and_caption(self) -> Tuple[Card, str]:
        print(f"{self.player_name} is giving a caption...")

        base64_cards = [self.encode_image(card.image) for card in self.cards_in_hand]
        messages = [
            {
                "role": "system",
                "content": "You are playing a game of Dixit. Your task is to select a card and return a caption for it. Return the index of the selected card as a number between 0 and N-1, where N is the number of cards. Return also the caption between quotes"
            }
        ]

        for idx, base64_image in enumerate(base64_cards):
            messages.append({
                "role": "user",
                "content": [{
                        "type": "text",
                        "text": f"This is card with index {idx}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            })

        data = {
            "model": "gpt-4o-mini",
            "messages": messages
        }

        
        max_retries = 3
        retries = 0

        while retries < max_retries:

            try:
                response = requests.post('https://api.openai.com/v1/chat/completions', headers=self.headers, json=data)
                response = response.json()

                content = response['choices'][0]["message"]['content']
                number_pattern = r'\d+'
                caption_pattern = r'"([^"]+)"'
                number_match = re.search(number_pattern, content)
                caption_match = re.search(caption_pattern, content)
                index = number_match.group() if number_match else None
                caption = caption_match.group() if caption_match else None
                caption = caption.replace("\"", "")

                index = int(index)

                card_to_play = self.cards_in_hand[index]
                self.cards_in_hand.remove(card_to_play)
                print(f"{self.player_name} selected a card with caption: \"{caption}\"")

                return card_to_play, caption
            except Exception  as e:
                retries += 1

                time.sleep(retries * 60)

        print("MAXIMUM RETRIES NUMBER REACHED. THE GPT BOT IS NOT AVAILABLE AT THE MOMENT. RETRY LATER.")
        sys.exit(1)
                

    
    def select_card_from_caption(self, caption: str) -> Card:
        print(f"{self.player_name} is selecting a card...")
        
        base64_cards = [self.encode_image(card.image) for card in self.cards_in_hand]
        messages = [
            {
                "role": "system",
                "content": "You are playing a game of Dixit. Your task is to select the best matching card for a given story prompt from the images provided. Return the index of the selected card as a number between 0 and N-1, where N is the number of cards."
            },
            {
                "role": "user",
                "content": f"The story prompt is: {caption}."
            }
        ]

        for idx, base64_image in enumerate(base64_cards):
            messages.append({
                "role": "user",
                "content": [{
                        "type": "text",
                        "text": f"This is card with index {idx}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            })

        data = {
            "model": "gpt-4o-mini",
            "messages": messages
        }

        max_retries = 3
        retries = 0

        while retries < max_retries:

            try:
                response = requests.post('https://api.openai.com/v1/chat/completions', headers=self.headers, json=data)
                response = response.json()

                content = response['choices'][0]["message"]['content']
                match = re.search(r'\d+', content)
                index = int(match.group())  

                selected_card = self.cards_in_hand[index]
                self.cards_in_hand.remove(selected_card)

                return selected_card
            
            except Exception  as e:
                retries += 1

                time.sleep(retries * 60)

        print("MAXIMUM RETRIES NUMBER REACHED. THE GPT BOT IS NOT AVAILABLE AT THE MOMENT. RETRY LATER.")
        sys.exit(1)
    
    def get_most_likely_card(self, cards_on_table: List[Tuple[Player, Card]], caption: str) -> Player:
        print(f"{self.player_name} is voting...")
        
        base64_cards = [self.encode_image(card.image) for _, card in cards_on_table]
        messages = [
            {
                "role": "system",
                "content": "You are playing a game of Dixit. Your task is to select the best matching card for a given story prompt from the images provided. Return the index of the selected card as a number between 0 and N-1, where N is the number of cards."
            },
            {
                "role": "user",
                "content": f"The story prompt is: {caption}."
            }
        ]

        for idx, base64_image in enumerate(base64_cards):
            messages.append({
                "role": "user",
                "content": [{
                        "type": "text",
                        "text": f"This is card with index {idx}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            })

        data = {
            "model": "gpt-4o-mini",
            "messages": messages
        }

        max_retries = 3
        retries = 0

        while retries < max_retries:

            try:
                response = requests.post('https://api.openai.com/v1/chat/completions', headers=self.headers, json=data)
                response = response.json()

                content = response['choices'][0]["message"]['content']
                match = re.search(r'\d+', content)
                index = int(match.group())  

                return cards_on_table[index][0]
            except Exception  as e:
                retries += 1

                time.sleep(retries * 60)
        
        print("MAXIMUM RETRIES NUMBER REACHED. THE GPT BOT IS NOT AVAILABLE AT THE MOMENT. RETRY LATER.")
        sys.exit(1)
