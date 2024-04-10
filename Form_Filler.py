import sys
import io

from datetime import datetime
from csv import DictReader

from PyPDF2 import PdfWriter, PdfReader

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def getFormData(filename):
    data_fields = []
    with open(filename, 'r') as fp:
        dr = DictReader(fp)
        data_fields = [row for row in dr]
        fp.close()
    
    return data_fields


def getLocations(filename):
    with open(filename, 'r') as fp:
        dr = DictReader(fp)
        locations = [row for row in dr]
        fp.close()
    
    return locations


def printFieldsForA1Medical(datafields, can, locations, page):

    # Register cursive font for signatures.
    pdfmetrics.registerFont(TTFont('CursiveBold', 'Cursive-standard-Bold.ttf'))

    # Loop through all field locations
    for loc in locations:
        try:
            can.setFont('Times-Roman', 12)

            # Check for Specifiers
            match loc["Specifier"]:
                case "Hyphen":
                    before, after = loc["Fill Field"].split("-")
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datafields[before] + "-" + datafields[after])
                case "Checkbox":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), "X")
                case "Signature":
                    can.setFont('CursiveBold', 12)
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datafields[loc["Fill Field"]])
                case "BillCityStateZip":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datafields["Billing City"] + ", " + datafields["Billing State"] + " " + datafields["Billing Zip Code"])
                case "ExpMonth":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datafields["Expiration Date"].split("/")[0])
                case "ExpYear":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datafields["Expiration Date"].split("/")[2])
                case "DateNow":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datetime.now().strftime("%m/%d/%y"))
                case "DateDay":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datetime.now().strftime("%d"))
                case "DateMonth":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datetime.now().strftime("%m"))
                case "DateYear":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datetime.now().strftime("%y"))
                case "Circle":
                    can.ellipse(inch * float(loc["X"]), inch * float(loc["y"]), inch * float(loc["X"]) + 1.5 * inch, inch * float(loc["y"]) + 0.25 * inch)
                case "Blank":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), "Blank")
                case "":
                    can.drawString(inch * float(loc["X"]), inch * float(loc["y"]), datafields[loc["Fill Field"]])
        except(KeyError):
            print(KeyError, loc["Form Entry"], " - ", loc["Fill Field"], " - ", loc["Specifier"])


if __name__ == "__main__":
    
    # Check input arguments
    if len(sys.argv) != 5:
        sys.exit("Usage: python3 Form_Filler.py <Google Form CSV> <Coordinates CSV> <Template PDF> <Output PDF>")
    
    # Read data fields from csv
    data_fields = getFormData(sys.argv[1])

    # Read data field locations from csv
    locations = getLocations(sys.argv[2])

    # Extract number of pages on form
    if "Page" in locations[0].keys():
        num_pages = int(max(locations, key=lambda x: int(x["Page"]))["Page"])
        pages_to_edit = list(set(int(entry["Page"]) for entry in locations))
    else:
        num_pages = 1
        pages_to_edit = [1]

    existing_pdf = PdfReader(open(sys.argv[3], "rb")) 
    output_stream = open(sys.argv[4], "wb")

    # Write output pages
    output = PdfWriter()
    for i in range(len(existing_pdf.pages)):
        # If page is not in pages_to_edit, merge it without changes
        if i + 1 not in pages_to_edit:
            output.add_page(existing_pdf.pages[i])
        else:
            # Initialize canvas to draw form field data
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            
            # Draw all form fields onto the canvas for this page
            printFieldsForA1Medical(data_fields[0], can, locations, i + 1)
            can.save()

            # Write template and canvas to output PDF
            packet.seek(0)
            new_pdf = PdfReader(packet)

            for page_num in range(len(new_pdf.pages)):
                page = existing_pdf.pages[i] if i < len(existing_pdf.pages) else existing_pdf.pages[-1]
                new_page = new_pdf.pages[page_num]
                page.merge_page(new_page)
                output.add_page(page)

    # Write the merged pages to the output PDF
    output.write(output_stream)
    
    # Close output stream
    output_stream.close()
    
    