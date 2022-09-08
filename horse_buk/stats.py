""" 
    Horse, jockey, trainer, stable rankings
"""
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
#from cStringIO import StringIO
from io import StringIO 
from pdfminer.high_level import extract_text_to_fp
output_string = StringIO()

pdfnamee = "currentPDF"

with open('currentPDF', 'rb') as fin:
     extra = extract_text_to_fp(fin, output_string, laparams=LAParams(),
                        output_type='text', codec="utf-8")
     print(extra)
     
print(output_string.getvalue().strip())



def pdf_to_text(pdfname):
    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    device = TextConverter(rsrcmgr)
    device = extract_text_to_fp(rsrcmgr, sio, codec='utf-8', laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
      # get text from file
    with open (pdfname, "rb") as fp:
        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
      # Get text from StringIO
        text = sio.getvalue()
      # close objects
    device.close()
    sio.close()

    return text
#pdf_to_text(pdfnamee)