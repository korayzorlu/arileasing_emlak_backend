"""Generates the "Tanıtım Broşürü" PNG by editing a copy of the original brochure PDF
directly — erasing the example numbers and inserting the live calculation's numbers as real
vector text (Poppins) at the exact coordinates the originals occupied, then rasterizing once
at high DPI. This keeps the output pixel-for-pixel identical to the source design (fonts,
icons, layout, colors) with no quality loss from client-side re-rendering.

Coordinates below are in the source PDF's 300dpi raster space (2550x3300 px for the
612x792pt page) — that's the space they were originally measured in against a rendered
copy of the PDF, so PX_PER_PT converts them to PDF points before drawing.
"""

import os

import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_TEMPLATE = os.path.join(BASE_DIR, "assets", "template.pdf")
FONT_BOLD = os.path.join(BASE_DIR, "assets", "fonts", "Poppins-ExtraBold.ttf")
FONT_MED = os.path.join(BASE_DIR, "assets", "fonts", "Poppins-Medium.ttf")

PX_PER_PT = 300 / 72.0
BG_COLOR = (249 / 255, 249 / 255, 249 / 255)
TEXT_COLOR = (0x12 / 255, 0x15 / 255, 0x2A / 255)
LINE_COLOR = (108 / 255, 113 / 255, 124 / 255)

BULLET_FONT_SIZE = 14
TABLE_FONT_SIZE = 12.5
ANNUAL_INFLATION_PERCENT = 25  # fixed TÜFE assumption used throughout the brochure copy

TABLE_ROW_Y = [(2411, 2491), (2494, 2572), (2574, 2655), (2657, 2745)]
TABLE_COL_X = [(380, 793), (800, 1245), (1251, 1722), (1728, 2157)]


def _px_to_pt(px: float) -> float:
    return px / PX_PER_PT


def _pmt(rate: float, nper: int, pv: float) -> float:
    if rate == 0:
        return pv / nper
    return (rate * pv) / (1 - (1 + rate) ** (-nper))


def _first_installment(price: float, down_payment: float, term_months: int, annual_rate_percent: float) -> float:
    loan = price - down_payment
    monthly_rate = (1 + annual_rate_percent / 100) ** (1 / 12) - 1
    return _pmt(monthly_rate, term_months, loan)


def _sum_stepped(first: float, annual_growth_percent: float, months: int) -> float:
    growth = annual_growth_percent / 100
    full_years = months // 12
    remainder = months % 12
    years_sum = full_years if growth == 0 else ((1 + growth) ** full_years - 1) / growth
    remainder_contribution = remainder * (1 + growth) ** full_years
    return first * (12 * years_sum + remainder_contribution)


def _round_to_clean_amount(value: float, step: int = 50_000) -> int:
    return round(value / step) * step


def _fmt(n: float, decimals: int = 0) -> str:
    n = round(n, decimals)
    s = f"{n:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _money(v: float) -> str:
    return f"{_fmt(v)} TL"


def _bullet_money(v: float) -> str:
    # Bullet copy rounds to the nearest thousand for a clean marketing figure — the table
    # still shows the exact number, matching the source brochure's own example.
    return _money(round(v / 1000) * 1000)


def _millions(v: float) -> str:
    return f"{_fmt(v / 1_000_000)} milyon TL"


class BrochureCalculationError(ValueError):
    pass


def compute(price: float, down_payment: float, term_months: int, annual_rate_percent: float) -> dict:
    if price <= 0 or term_months <= 0:
        raise BrochureCalculationError("Geçersiz hesaplama girdileri.")

    first_inst = _first_installment(price, down_payment, term_months, annual_rate_percent)
    real_sale = down_payment + first_inst * term_months
    nominal = down_payment + _sum_stepped(first_inst, ANNUAL_INFLATION_PERCENT, term_months)
    nominal_rounded = round(nominal / 1_000_000) * 1_000_000

    rows = []
    for term in (120, 60):
        for pct in (30, 50):
            dp = _round_to_clean_amount(price * pct / 100)
            fi = _first_installment(price, dp, term, annual_rate_percent)
            rows.append(
                {
                    "down_payment": dp,
                    "term_months": term,
                    "first_installment": fi,
                    "real_sale_price": dp + fi * term,
                }
            )

    return {
        "price": price,
        "real_sale_price": real_sale,
        "down_payment": down_payment,
        "term_months": term_months,
        "first_installment": first_inst,
        "nominal_income_rounded": nominal_rounded,
        "annual_rate_percent": annual_rate_percent,
        "rows": rows,
    }


_font_cache: dict[str, "fitz.Font"] = {}


def _font(fontfile: str) -> "fitz.Font":
    if fontfile not in _font_cache:
        _font_cache[fontfile] = fitz.Font(fontfile=fontfile)
    return _font_cache[fontfile]


def _fit_size(fontfile: str, text: str, fontsize: float, max_width_pt: float, floor: float = 8) -> float:
    size = fontsize
    while size > floor and _font(fontfile).text_length(text, fontsize=size) > max_width_pt:
        size -= 0.5
    return size


def _erase(page, x0, y0, x1, y1, pad=6):
    rect = fitz.Rect(_px_to_pt(x0 - pad), _px_to_pt(y0 - pad), _px_to_pt(x1 + pad), _px_to_pt(y1 + pad))
    page.draw_rect(rect, color=None, fill=BG_COLOR)


def _insert_left(page, x0, x1, y_baseline_px, text, fontsize=BULLET_FONT_SIZE, fontfile=FONT_BOLD):
    max_width = _px_to_pt(x1) - _px_to_pt(x0) - 2
    size = _fit_size(fontfile, text, fontsize, max_width)
    page.insert_text(
        fitz.Point(_px_to_pt(x0), _px_to_pt(y_baseline_px)),
        text,
        fontsize=size,
        fontfile=fontfile,
        fontname="ov-bold",
        color=TEXT_COLOR,
    )


def _insert_center(page, x0, x1, y0, y1, text, fontsize=TABLE_FONT_SIZE, fontfile=FONT_MED):
    max_width = _px_to_pt(x1) - _px_to_pt(x0)
    size = _fit_size(fontfile, text, fontsize, max_width)
    w = _font(fontfile).text_length(text, fontsize=size)
    cx = _px_to_pt(x0) + (_px_to_pt(x1) - _px_to_pt(x0) - w) / 2
    baseline_y = _px_to_pt(y1) - 5
    page.insert_text(
        fitz.Point(cx, baseline_y), text, fontsize=size, fontfile=fontfile, fontname="ov-med", color=TEXT_COLOR
    )


def generate_brochure_jpeg(
    price: float, down_payment: float, term_months: int, annual_rate_percent: float, dpi: int = 300
) -> bytes:
    data = compute(price, down_payment, term_months, annual_rate_percent)

    doc = fitz.open(PDF_TEMPLATE)
    try:
        page = doc[0]

        erase_regions = [
            (1580, 916, 1840, 995),  # bullet 1: TÜFE+%rate (extra headroom for the Ü's dots)
            (995, 1270, 1425, 1350),  # bullet 3 line 1: price
            (775, 1355, 1282, 1435),  # bullet 3 line 2: real sale price
            (855, 1465, 1252, 1550),  # bullet 4 line 1: down payment
            (1638, 1465, 1746, 1535),  # bullet 4 line 1: term
            (490, 1550, 796, 1620),  # bullet 4 line 2: first installment
            (490, 1790, 616, 1863),  # bullet 6 line 1: term
            (1424, 1790, 1566, 1863),  # bullet 6 line 1: inflation %
            (1114, 1878, 1516, 1960),  # bullet 6 line 2: nominal income
        ]
        for region in erase_regions:
            _erase(page, *region)
        for ry0, ry1 in TABLE_ROW_Y:
            for cx0, cx1 in TABLE_COL_X:
                _erase(page, cx0, ry0 + 2, cx1, ry1 - 2, pad=0)

        for x in (796, 1248, 1725):
            page.draw_line(
                fitz.Point(_px_to_pt(x), _px_to_pt(2411)),
                fitz.Point(_px_to_pt(x), _px_to_pt(2745)),
                color=LINE_COLOR,
                width=_px_to_pt(2),
            )
        for y in (2492, 2573, 2656):
            page.draw_line(
                fitz.Point(_px_to_pt(377), _px_to_pt(y)),
                fitz.Point(_px_to_pt(2160), _px_to_pt(y)),
                color=LINE_COLOR,
                width=_px_to_pt(2),
            )

        _insert_left(page, 1580, 1840, 988, f"TÜFE+%{_fmt(data['annual_rate_percent'])}")
        _insert_left(page, 995, 1425, 1340, _bullet_money(data["price"]))
        _insert_left(page, 775, 1282, 1425, _bullet_money(data["real_sale_price"]) + "'ye")
        _insert_left(page, 855, 1252, 1538, _money(data["down_payment"]))
        _insert_left(page, 1638, 1746, 1528, f"{data['term_months']}")
        _insert_left(page, 490, 796, 1610, _money(data["first_installment"]))
        _insert_left(page, 490, 616, 1853, f"{data['term_months']}")
        _insert_left(page, 1424, 1566, 1853, f"%{_fmt(ANNUAL_INFLATION_PERCENT)}")
        _insert_left(page, 1114, 1516, 1950, _millions(data["nominal_income_rounded"]))

        for i, row in enumerate(data["rows"]):
            ry0, ry1 = TABLE_ROW_Y[i]
            cols = TABLE_COL_X
            _insert_center(page, *cols[0], ry0, ry1, _fmt(row["down_payment"]))
            _insert_center(page, *cols[1], ry0, ry1, f"{row['term_months']} ay")
            _insert_center(page, *cols[2], ry0, ry1, _fmt(row["first_installment"]))
            _insert_center(page, *cols[3], ry0, ry1, _fmt(row["real_sale_price"]))

        zoom = dpi / 72.0
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        # JPEG: this page has no transparency and is mostly flat color + text, so quality
        # loss is imperceptible while the payload drops by roughly 6x versus PNG — matters
        # since this rides over a mobile connection as a base64 JSON response.
        return pix.tobytes("jpeg", jpg_quality=92)
    finally:
        doc.close()
