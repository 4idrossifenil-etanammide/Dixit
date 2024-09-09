import re

text = 'The caption is 5 and the card number is "AAA"'

# Regular expression to find the number
number_pattern = r'\d+'

# Regular expression to find the caption inside quotes
caption_pattern = r'"([^"]+)"'

# Find the first occurrence of a number
number_match = re.search(number_pattern, text)

# Find the first occurrence of a caption within quotes
caption_match = re.search(caption_pattern, text)

# Extract the matches if they exist
number = number_match.group() if number_match else None
caption = caption_match.group() if caption_match else None
caption = caption.replace("\"", "")


print(f"Number: {number}")
print(f"Caption: {caption}")