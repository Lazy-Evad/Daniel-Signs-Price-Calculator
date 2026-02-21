from fpdf import FPDF
from datetime import datetime


# ── Unicode sanitiser ─────────────────────────────────────────────────────────
# fpdf2 Helvetica/Times/Courier are Latin-1 only. Replace common Unicode chars.
_UNICODE_MAP = {
    '\u2014': '-', '\u2013': '-',     # em-dash, en-dash
    '\u2018': "'", '\u2019': "'",     # curly single quotes
    '\u201c': '"', '\u201d': '"',     # curly double quotes
    '\u2026': '...',                  # ellipsis
    '\u00d7': 'x',                   # multiplication sign (x)
    '\u2022': '*',                   # bullet
    '\u2713': 'OK', '\u2714': 'OK',  # check marks
    '\u00f7': '/',                   # division sign
    '\u00b1': '+/-',                 # plus-minus
    '\u2192': '->',                  # right arrow
    '\u00b2': '2',                   # superscript 2 (m2)
    '\u00b3': '3',                   # superscript 3
    '\u00a3': 'GBP',                 # pound sign (in descriptions)
    '\u00e9': 'e',                   # e with accent
    '\u00e8': 'e',                   # e with grave
    '\u00e0': 'a',                   # a with grave
    '\u00fc': 'u',                   # u with umlaut
    '\u00f6': 'o',                   # o with umlaut
    '\u00e4': 'a',                   # a with umlaut
}

def safe(text):
    """Convert any value to a Latin-1-safe string for fpdf Helvetica rendering."""
    s = str(text) if text is not None else ''
    for ch, rep in _UNICODE_MAP.items():
        s = s.replace(ch, rep)
    # Drop any remaining non-Latin-1 characters rather than crashing
    return s.encode('latin-1', errors='replace').decode('latin-1')


# ── PDF Class ─────────────────────────────────────────────────────────────────

class CostReportPDF(FPDF):

    def header(self):
        # Dark red brand bar at top
        self.set_fill_color(30, 30, 30)
        self.rect(0, 0, 210, 4, 'F')
        self.ln(6)

        # Left: Company name
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(245, 158, 11)          # orange
        self.cell(110, 9, 'DANIEL SIGNS', ln=0)

        # Right: Document type - clearly internal
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(180, 50, 50)           # dark red
        self.cell(0, 9, 'INTERNAL COST REPORT', ln=1, align='R')

        self.set_font('helvetica', '', 9)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, 'CONFIDENTIAL - Not for client distribution', ln=1, align='R')

        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-13)
        self.set_draw_color(220, 220, 220)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font('helvetica', 'I', 7.5)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8,
                  safe(f'INTERNAL - Daniel Signs Cost Report  |  Page {self.page_no()}  |  '
                  f'Generated {datetime.now().strftime("%d/%m/%Y %H:%M")}'),
                  align='C')

    # ── Shared helpers ────────────────────────────────────────────────────────

    def section_heading(self, title, bg=(240, 240, 240), text_color=(30, 30, 30)):
        self.set_fill_color(*bg)
        self.set_text_color(*text_color)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 7, safe(f'  {title}'), ln=1, fill=True, border=0)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def table_header(self, cols):
        """cols: list of (label, width)"""
        self.set_fill_color(40, 40, 40)
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 8.5)
        for i, (label, w) in enumerate(cols):
            align = 'R' if i > 0 else 'L'
            s = safe(label)
            self.cell(w, 7, f'  {s}' if align == 'L' else s, fill=True, align=align, border=0)
        self.ln()
        self.set_text_color(30, 30, 30)

    def table_row(self, values, widths, row_idx=0, bold=False):
        """values and widths are parallel lists; first col left-aligned, rest right"""
        fill_color = (252, 252, 252) if row_idx % 2 == 0 else (244, 244, 244)
        self.set_fill_color(*fill_color)
        self.set_font('helvetica', 'B' if bold else '', 9)
        for i, (val, w) in enumerate(zip(values, widths)):
            align = 'R' if i > 0 else 'L'
            s = safe(val)
            self.cell(w, 6, f'  {s}' if align == 'L' else f'{s}  ', fill=True, border='B', align=align)
        self.ln()

    def kv(self, label, value, label_w=100, bold_val=False):
        self.set_font('helvetica', '', 9.5)
        self.set_text_color(80, 80, 80)
        self.cell(label_w, 6, safe(label))
        self.set_font('helvetica', 'B' if bold_val else '', 9.5)
        self.set_text_color(20, 20, 20)
        self.cell(0, 6, safe(value), ln=1)
        self.set_text_color(0, 0, 0)

    def big_total_row(self, label, value, color=(40, 40, 40), text_color=(255, 255, 255)):
        self.set_fill_color(*color)
        self.set_text_color(*text_color)
        self.set_font('helvetica', 'B', 12)
        self.cell(130, 11, safe(f'  {label}'), fill=True)
        self.cell(60, 11, safe(f'{value}  '), fill=True, align='R', ln=1)
        self.set_text_color(0, 0, 0)


# ── Public entry point ─────────────────────────────────────────────────────────

def generate_quote_pdf(client_info, items, results, markup,
                       created_by='Unknown', timestamp=None,
                       labour_hours=None):
    """
    Generate an internal cost report PDF.

    Parameters
    ----------
    client_info  : dict   - name, contact, description
    items        : list   - job_items from session state
    results      : dict   - output of PricingEngine.calculate_job()
    markup       : float  - markup multiplier (e.g. 2.5)
    created_by   : str    - logged-in user name
    timestamp    : datetime | None
    labour_hours : dict | None  - {prod, inst, trav, design, fitters}
                                  (hours aren't echoed by the engine so passed separately)
    """
    if timestamp is None:
        timestamp = datetime.now()
    if labour_hours is None:
        labour_hours = {}

    # ── Unpack results ────────────────────────────────────────────────────────
    mat_raw          = results.get('material_cost_raw', 0)          # before wastage
    wastage_cost     = results.get('wastage_cost', 0)
    mat_total        = results.get('material_cost_total', 0)        # after wastage, before markup
    shop_int         = results.get('shop_cost_internal', 0)         # prod+design internal cost
    inst_int         = results.get('install_cost_internal', 0)
    trav_int         = results.get('travel_cost_internal', 0)
    breakeven        = results.get('breakeven', 0)
    workshop_billed  = results.get('workshop_price_billed', 0)
    install_billed   = results.get('install_price_billed', 0)
    travel_billed    = results.get('travel_price_billed', 0)
    labour_billed    = results.get('labor_total_billed', 0)
    quote_price      = results.get('quote_price', 0)
    profit           = results.get('profit', 0)
    design_h_billed  = results.get('design_hours_billed', 0)
    design_h_input   = results.get('design_hours_input', 0)
    print_ready      = results.get('print_ready', False)
    repeat_job       = results.get('repeat_job', False)
    nesting_on       = results.get('nesting_enabled', False)

    # Hours (passed separately)
    prod_h    = labour_hours.get('prod', 0)
    inst_h    = labour_hours.get('inst', 0)
    trav_h    = labour_hours.get('trav', 0)
    design_h  = labour_hours.get('design', design_h_billed)
    fitters   = labour_hours.get('fitters', 1)

    margin_pct = (profit / quote_price * 100) if quote_price > 0 else 0
    markup_pct = (markup - 1) * 100   # e.g. markup=2.5 -> 150%

    # ── Client info (sanitised for Latin-1) ─────────────────────────────────
    client_name = safe(client_info.get('name', '') or 'N/A')
    client_ref  = safe(client_info.get('contact', '') or '')
    job_desc    = safe(client_info.get('description', '') or '')

    material_items = [i for i in items if i.get('type') == 'material']
    labour_items   = [i for i in items if i.get('type') == 'labor']
    total_qty      = sum(i.get('qty', 1) for i in material_items)

    # ── Build PDF ─────────────────────────────────────────────────────────────
    pdf = CostReportPDF()
    pdf.add_page()

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 0 - Report header box (meta)
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.set_fill_color(250, 246, 240)
    pdf.set_draw_color(235, 210, 180)
    box_y = pdf.get_y()
    pdf.rect(10, box_y, 190, 26, 'FD')
    pdf.set_y(box_y + 3)

    left_items  = [('Prepared by:', safe(created_by)), ('Date:', timestamp.strftime('%d %B %Y'))]
    right_items = [('Time:', timestamp.strftime('%H:%M')), ('Ref / Contact:', client_ref or '-')]

    for (ll, lv), (rl, rv) in zip(left_items, right_items):
        pdf.set_x(14)
        pdf.set_font('helvetica', '', 8.5); pdf.set_text_color(110, 110, 110)
        pdf.cell(22, 5, ll)
        pdf.set_font('helvetica', 'B', 8.5); pdf.set_text_color(20, 20, 20)
        pdf.cell(68, 5, lv)
        pdf.set_font('helvetica', '', 8.5); pdf.set_text_color(110, 110, 110)
        pdf.cell(20, 5, rl)
        pdf.set_font('helvetica', 'B', 8.5); pdf.set_text_color(20, 20, 20)
        pdf.cell(0, 5, rv, ln=1)

    pdf.ln(6)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 1 - Job / Client Details
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.section_heading('1. JOB & CLIENT DETAILS', bg=(245, 158, 11), text_color=(255, 255, 255))
    pdf.kv('Client Name:', client_name)
    if client_ref:
        pdf.kv('Contact / Reference:', client_ref)
    if job_desc:
        pdf.set_font('helvetica', '', 9.5); pdf.set_text_color(80, 80, 80)
        pdf.cell(100, 6, 'Job Description:')
        pdf.set_text_color(20, 20, 20)
        pdf.multi_cell(0, 5, job_desc)
    # Job flags
    flags = []
    if print_ready: flags.append('Print-Ready Artwork (no design time)')
    if repeat_job:  flags.append('Repeat Job (no design time)')
    if nesting_on:  flags.append('Nesting Optimiser Enabled')
    if flags:
        pdf.set_font('helvetica', 'I', 9); pdf.set_text_color(100, 100, 150)
        pdf.cell(0, 5, 'Flags: ' + '  |  '.join(flags), ln=1)
    pdf.ln(4)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2 - Materials
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.section_heading('2. MATERIALS SELECTED', bg=(50, 50, 50), text_color=(255, 255, 255))

    col_w = [90, 22, 22, 28, 28]   # Desc | W | H | Qty | Item
    pdf.table_header([
        ('Description / Material', col_w[0]),
        ('Width', col_w[1]),
        ('Height', col_w[2]),
        ('Qty', col_w[3]),
        ('Area (m2)', col_w[4]),
    ])
    for ri, item in enumerate(material_items):
        desc = item.get('description', 'Unknown')
        w_m  = item.get('width', 0)
        h_m  = item.get('height', 0)
        qty  = item.get('qty', 1)
        # If nesting, show optimised area; else standard
        if nesting_on and 'nesting_area_m2' in item:
            area = item['nesting_area_m2']
        else:
            area = w_m * h_m * qty
        pdf.table_row(
            [desc, f'{w_m*100:.1f}cm', f'{h_m*100:.1f}cm', str(qty), f'{area:.4f}'],
            col_w, row_idx=ri
        )

    if labour_items:
        pdf.set_font('helvetica', 'I', 8); pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 5, '  Additional labour items also included (see Section 3)', ln=1)

    pdf.ln(3)
    # Material cost sub-table
    pdf.set_font('helvetica', '', 9.5); pdf.set_text_color(60, 60, 60)
    cost_rows = [
        ('Raw material cost (area x rate/m2):', f'£{mat_raw:,.2f}'),
        (f'Wastage allowance added:', f'£{wastage_cost:,.2f}'),
        ('Material subtotal (inc. wastage):', f'£{mat_total:,.2f}'),
    ]
    for lbl, val in cost_rows:
        pdf.kv(lbl, val)
    pdf.ln(4)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3 - Labour & Time
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.section_heading('3. LABOUR & TIME COSTS', bg=(50, 50, 50), text_color=(255, 255, 255))

    lab_col_w = [65, 22, 32, 35, 36]
    pdf.table_header([
        ('Category', lab_col_w[0]),
        ('Hours', lab_col_w[1]),
        ('Internal Rate', lab_col_w[2]),
        ('Internal Cost', lab_col_w[3]),
        ('Billed Cost', lab_col_w[4]),
    ])

    labour_table_rows = []
    ri = 0

    # Design / Artwork
    if design_h > 0:
        from_shop = shop_int   # design + prod combined in engine; split where possible
        # Design billed is included in workshop_billed total
        labour_table_rows.append((
            'Design / Artwork',
            f'{design_h:.1f}h',
            'Shop overhead rate',
            '(in production total)',
            '(in workshop total)'
        ))

    # Production / Workshop (inc. design if any)
    if prod_h > 0 or design_h > 0:
        total_prod_h = prod_h + design_h
        labour_table_rows.append((
            f'Production / Workshop (incl. design)',
            f'{total_prod_h:.1f}h',
            'Shop + Workshop rates',
            f'£{shop_int:,.2f}',
            f'£{workshop_billed:,.2f}',
        ))
    elif shop_int > 0:
        labour_table_rows.append((
            'Production / Workshop',
            '-',
            'Shop + Workshop rates',
            f'£{shop_int:,.2f}',
            f'£{workshop_billed:,.2f}',
        ))

    # Installation
    if inst_h > 0:
        labour_table_rows.append((
            f'Installation ({fitters} fitter{"s" if fitters != 1 else ""})',
            f'{inst_h:.1f}h',
            'Fitting rate',
            f'£{inst_int:,.2f}',
            f'£{install_billed:,.2f}',
        ))
    elif inst_int > 0:
        labour_table_rows.append((
            'Installation',
            '-',
            'Fitting rate',
            f'£{inst_int:,.2f}',
            f'£{install_billed:,.2f}',
        ))

    # Travel
    if trav_h > 0:
        labour_table_rows.append((
            'Travel',
            f'{trav_h:.1f}h',
            'Travel rate',
            f'£{trav_int:,.2f}',
            f'£{travel_billed:,.2f}',
        ))
    elif trav_int > 0:
        labour_table_rows.append((
            'Travel',
            '-',
            'Travel rate',
            f'£{trav_int:,.2f}',
            f'£{travel_billed:,.2f}',
        ))

    # Additional ad-hoc labour items
    for litem in labour_items:
        ldesc = litem.get('description', 'Additional Labour')
        lab_d = litem.get('raw_labor', {})
        extra_h = lab_d.get('prod', 0) + lab_d.get('inst', 0) + lab_d.get('trav', 0)
        labour_table_rows.append((ldesc, f'{extra_h:.1f}h', '-', '(included in totals)', '(included in totals)'))

    for ri, row in enumerate(labour_table_rows):
        pdf.table_row(list(row), lab_col_w, row_idx=ri)

    # Totals row
    l_internal_total = shop_int + inst_int + trav_int
    pdf.set_fill_color(235, 235, 235)
    pdf.set_font('helvetica', 'B', 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(lab_col_w[0], 7, '  TOTAL LABOUR', fill=True)
    pdf.cell(lab_col_w[1], 7, '', fill=True)
    pdf.cell(lab_col_w[2], 7, '', fill=True)
    pdf.cell(lab_col_w[3], 7, f'£{l_internal_total:,.2f}  ', fill=True, align='R')
    pdf.cell(lab_col_w[4], 7, f'£{labour_billed:,.2f}  ', fill=True, align='R', ln=1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 4 - Cost to Produce (Breakeven)
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.section_heading('4. COST TO PRODUCE (BREAKEVEN)', bg=(50, 50, 50), text_color=(255, 255, 255))

    produce_rows = [
        ('Material Cost (inc. wastage):', f'£{mat_total:,.2f}'),
        ('Labour - Internal / Overhead Cost:', f'£{l_internal_total:,.2f}'),
    ]
    for lbl, val in produce_rows:
        pdf.kv(lbl, val)

    pdf.ln(1)
    pdf.big_total_row('TOTAL COST TO PRODUCE', f'£{breakeven:,.2f}', color=(60, 60, 60))
    pdf.ln(5)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 5 - Client Quote Price (with Markup)
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.section_heading('5. CLIENT QUOTE PRICE (WITH MARKUP)', bg=(50, 50, 50), text_color=(255, 255, 255))

    quote_rows = [
        ('Material Cost x Markup:', f'£{mat_total:,.2f}  x  {markup:.2f}  =  £{mat_total*markup:,.2f}'),
        ('Labour Billed to Client:', f'£{labour_billed:,.2f}'),
        (f'Markup Applied ({markup_pct:.0f}% above cost on materials):', f'x{markup:.2f}'),
    ]
    for lbl, val in quote_rows:
        pdf.kv(lbl, val)

    pdf.ln(2)
    pdf.big_total_row('CLIENT QUOTE PRICE', f'£{quote_price:,.2f}', color=(245, 158, 11))
    pdf.ln(4)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 6 - Profit & Margin Summary
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.section_heading('6. PROFIT & MARGIN SUMMARY', bg=(50, 50, 50), text_color=(255, 255, 255))

    summary_rows = [
        ('Cost to Produce (Breakeven):',    f'£{breakeven:,.2f}',     False),
        ('Client Quote Price:',             f'£{quote_price:,.2f}',   False),
        ('Gross Profit:',                   f'£{profit:,.2f}',         True),
        ('Profit Margin %:',                f'{margin_pct:.1f}%',      True),
        ('Markup Multiplier Applied:',      f'x{markup:.2f}  ({markup_pct:.0f}% above mat. cost)', False),
    ]
    for lbl, val, bold in summary_rows:
        pdf.kv(lbl, val, bold_val=bold)

    pdf.ln(3)

    # ── Per-item economics (if qty > 0) ───────────────────────────────────────
    if total_qty > 0 and quote_price > 0:
        pdf.section_heading('7. PER-ITEM ECONOMICS', bg=(50, 50, 50), text_color=(255, 255, 255))
        ue_col_w = [80, 37, 37, 36]
        pdf.table_header([
            ('Component', ue_col_w[0]),
            (f'Per Item (/{total_qty})', ue_col_w[1]),
            (f'Total (x{total_qty})', ue_col_w[2]),
            ('% of Quote', ue_col_w[3]),
        ])
        ue_rows = [
            ('Material (inc. wastage)',  mat_total / total_qty,   mat_total,        round(mat_total / quote_price * 100, 1) if quote_price else 0),
            ('Labour (billed)',           labour_billed / total_qty, labour_billed,  round(labour_billed / quote_price * 100, 1) if quote_price else 0),
            ('Cost to Produce',           breakeven / total_qty,   breakeven,        round(breakeven / quote_price * 100, 1) if quote_price else 0),
            ('Quote Price (sell)',         quote_price / total_qty, quote_price,     100.0),
            ('Profit',                    profit / total_qty,       profit,           round(margin_pct, 1)),
        ]
        for ri, (lbl, per, tot, pct) in enumerate(ue_rows):
            bold = ri in (3, 4)
            pdf.table_row(
                [lbl, f'£{per:,.2f}', f'£{tot:,.2f}', f'{pct:.1f}%'],
                ue_col_w, row_idx=ri, bold=bold
            )
        pdf.ln(5)

    # ── Confidentiality footer note ────────────────────────────────────────────
    pdf.set_font('helvetica', 'B', 8)
    pdf.set_text_color(180, 50, 50)
    pdf.cell(0, 5, 'CONFIDENTIAL - This document contains internal cost data and must not be shared with clients.', ln=1, align='C')

    return bytes(pdf.output())
