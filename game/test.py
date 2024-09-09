from gpt_bot import GPT_bot
import os
from PIL import Image

from card import Card

import matplotlib.pyplot as plt

if __name__ == "__main__":
    path_to_images = "./images"

    deck = list()
    for image_name in os.listdir(path_to_images):
        image_number = int(image_name.split(".")[0])
        image = Image.open(os.path.join(path_to_images, image_name)).convert("RGB")
        card = Card(image_number, image)
        deck.append(card)
    
    #api_key = "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"
    api_key = "sk-4MLxSftMmbNLZMX03r9PmPVeRBK5g1Stk4eA9vfL1fT3BlbkFJ2Qrt9wO8yoEsRmi3IaBM7gtgEOiix0-fL7X-Q2ia0A"
    gpt = GPT_bot("gpt", 30, api_key)

    gpt.draw_initial_hand(deck)

    for card in gpt.cards_in_hand:
        plt.imshow(card.image)
        plt.show()

    caption = input("Insert caption")

    selected = gpt.select_card_from_caption(caption)

    plt.imshow(selected.image)
    plt.show()