from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTChar, LTTextLine
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

import io
import sys
from PyPDF2 import PdfWriter, PdfReader


target_text = [":", "_"]
coordinates = [
    #(39.352, 726.00852, 1),
    #(133.94, 625.18, 2),
    (139.82, 625.18, 3),
    #(131.42, 569.26, 4),
    (137.42, 569.26, 5),
    (84.984, 539.86, 6),
    (56.028, 519.19, 7),
    #(144.264, 498.55, 8),
    (150.26, 498.55, 9),
    #(111.288, 477.91, 10),
    (117.38, 477.91, 11),
    #(56.04, 457.27, 12),
    (62.04, 457.27, 13),
    #(110.592, 436.63, 14),
    (116.66, 436.63, 15),
    #(176.06, 390.31, 16),
    (182.06, 390.31, 17),
    (108.02, 369.67, 18),
    (108.02, 349.01, 19),
    #(178.70400000000004, 313.73, 20),
    (184.7, 313.73, 21),
    #(164.9, 269.81, 22),
    (170.9, 269.81, 23),
    #(248.81, 185.93, 24),
    (254.81, 185.93, 25),
    #(37.56, 72.50399999999999, 26),
]


# Step 1: Generate a 'stamp' PDF with the text in the right locations
def create_stamp_pdf(output_pdf_path, text_data, coordinates):
    c = canvas.Canvas(output_pdf_path, pagesize=letter)
    for (x_lower_left, y_lower_left, x_upper_right, y_upper_right), text in text_data:
        # You might want to compute the center or a proper starting point based on the bbox
        #c.rect(x_lower_left, y_lower_left, x_upper_right - x_lower_left, y_upper_right - y_lower_left, stroke=1, fill=1)
        c.drawString(x_lower_left, y_lower_left, text)  # Position the text at the coordinates
    #c.rect(133.94, 625.18, 137.0 - 133.94, 628.0 - 625.18, stroke=1, fill=1)

    for coords in coordinates:
        c.rect(coords[0] + 1.0, coords[1] + 1.0, 5.0, 5.0, stroke=1, fill=1)

    c.save()


def extract_coordinates():
    text_data = []
    for page_layout in extract_pages(pdf_file_path):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                text =  element.get_text().strip().split(':')[0].split('\n')[0].strip()
                if not text:
                    continue
                text_data.append(((element.bbox), text))

    return text_data


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
    i = 1
    for cc in character_coordinates:
        print(cc, "  ", i)
        i += 1
    return character_coordinates


def generate_boxed_copy(infile, outfile):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Times-Roman", 12)

    # Test
    can.drawString(inch * 1.94, inch * 8.75, "ADOBE")
    #coordinates = find_character_coordinates(infile, target_text)
    #for coords in coordinates:
    #    can.drawString(coords[0], coords[1], "Text" + str(coords[2]))
    can.save()
    
    packet.seek(0)
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(open(infile, "rb"))

    output = PdfWriter()

    for i in range(len(existing_pdf.pages)):
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
    
    output_stream = open(outfile, "wb")
    output.write(output_stream)
    output_stream.close()


if __name__ == "__main__":
    pdf_file_path = 'Garrison/forms/A1-Credit-Card-Auth-Form-2023Update.pdf'
    output_stamp_pdf = 'Garrison/forms/boxes.pdf'

    generate_boxed_copy(pdf_file_path, output_stamp_pdf)

    #coordinates = find_character_coordinates(pdf_file_path, target_text)
    #text_data = extract_coordinates()
    #create_stamp_pdf(output_stamp_pdf, text_data, coordinates)