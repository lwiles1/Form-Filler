import sys
from csv import DictReader

from PyPDF2 import PdfWriter, PdfReader
import io
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


def printFieldsForA1Medical(datafields, can):
    # Draw Signature
    pdfmetrics.registerFont(TTFont('CursiveBold', 'Cursive-standard-Bold.ttf'))
    can.setFont('CursiveBold', 16)
    can.drawString(0.5 * inch, 1.7 * inch, datafields["Name of Authorized Signatory"][:20])

    # Draw Print Name
    can.setFont('Times-Roman', 11)
    can.drawString(300, 150, datafields["Name of Authorized Signatory"])

    # Draw Title
    can.drawString(500, 150, datafields["Title of Authorized Signatory"])


if __name__ == "__main__":
    data_fields = getFormData(sys.argv[1])

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    printFieldsForA1Medical(data_fields[0], can)
    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(open(sys.argv[2], "rb"))

    output = PdfWriter()

    for i in range(len(existing_pdf.pages)):
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
    
    output_stream = open(sys.argv[3], "wb")
    output.write(output_stream)
    output_stream.close()
    