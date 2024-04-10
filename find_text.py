from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTChar, LTTextLine

def find_character_coordinates(pdf_path, target_text):
    character_coordinates = []
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                text = element.get_text()
                for tt in target_text:
                    if tt in text:
                        # Calculate the offset of the target text within the textbox
                        offset = text.index(tt)
                        # Iterate through the characters to find the target text
                        for text_obj in element:
                            if isinstance(text_obj, LTTextLine):
                                for char_obj in text_obj:
                                    if isinstance(char_obj, LTChar):
                                        if char_obj.get_text() == tt:
                                            # Calculate the coordinates of the character
                                            x, y = char_obj.bbox[0], char_obj.bbox[1]
                                            character_coordinates.append((x, y))
                                            break  # No need to continue searching
    return character_coordinates

# Example usage
pdf_path = 'Garrison/forms/A1-Credit-Card-Auth-Form-2023Update.pdf'
target_text = [":", "_"]
coordinates = find_character_coordinates(pdf_path, target_text)
print("Coordinates of '{}' in the PDF:".format(target_text))
for coord in coordinates:
    print("x={}, y={}".format(coord[0], coord[1]))
