from fpdf import FPDF
from datetime import datetime

class QuotePDF(FPDF):
    def header(self):
        # Company Branding
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(245, 158, 11) # Orange accent #f59e0b
        self.cell(0, 10, 'DANIEL SIGNS', ln=1, align='L')
        
        self.set_font('helvetica', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Professional Signage Solutions', ln=1, align='L')
        
        # Reset color and position for 'Quotation' label
        self.set_y(10)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'QUOTATION', ln=1, align='R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%d/%m/%Y %H:%M")}', align='C')

def generate_quote_pdf(client_info, items, results, markup):
    # fpdf2's output() returns bytes by default when no dest is provided
    pdf = QuotePDF()
    pdf.add_page()
    
    # 1. Client Info Section
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 8, 'CLIENT DETAILS:', ln=1)
    pdf.set_font('helvetica', '', 10)
    
    name = str(client_info.get('name', 'N/A'))
    contact = str(client_info.get('contact', 'N/A'))
    
    pdf.cell(30, 6, 'Name:', border=0)
    pdf.cell(0, 6, name, ln=1)
    pdf.cell(30, 6, 'Contact/Ref:', border=0)
    pdf.cell(0, 6, contact, ln=1)
    
    if client_info.get('description'):
        pdf.ln(2)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(0, 6, 'Project Description:', ln=1)
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 5, str(client_info.get('description')))
    
    pdf.ln(10)
    
    # 2. Table Header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(110, 8, ' Description', border=1, fill=True)
    pdf.cell(80, 8, ' Included', border=1, fill=True, ln=1)
    
    # 3. Items
    pdf.set_font('helvetica', '', 9)
    for item in items:
        desc = item.get('description', 'Unnamed Item')
        pdf.cell(110, 8, f' {desc}', border=1)
        pdf.cell(80, 8, ' Yes', border=1, ln=1)
    
    if not items:
        pdf.cell(190, 8, ' No items listed', border=1, ln=1, align='C')
    
    pdf.ln(10)
    
    # 4. Summary & Pricing
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 8, 'PROJECT TOTAL:', ln=1)
    
    # Final Total Box
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_fill_color(255, 245, 230) # Very light orange
    
    price_val = results.get("quote_price", 0)
    pdf.cell(140, 12, ' TOTAL QUOTED PRICE (GBP)', border=1, fill=True)
    pdf.cell(50, 12, f'GBP {price_val:,.2f} ', border=1, fill=True, ln=1, align='R')
    
    pdf.ln(10)
    pdf.set_font('helvetica', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    terms = "This quote is valid for 30 days. Prices are subject to final site survey and design approval. Thank you for choosing Daniel Signs."
    pdf.multi_cell(0, 5, terms)
    
    # Return as raw bytes for Streamlit
    return bytes(pdf.output())
