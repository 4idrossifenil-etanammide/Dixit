from PIL import Image

class Card():
    def __init__(self, image_number: int, image: Image.Image):
        self.image_number = image_number
        self.image = image

    def __repr__(self) -> str:
        return str(self.image_number)
