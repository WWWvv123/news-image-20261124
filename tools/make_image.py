#!/usr/bin/env python3
"""Draw a classic newspaper front page for Tuesday, 24 November 2026.

Everything on the page - masthead, headlines, summaries, rules - is drawn
with Pillow. Run from the entry directory (or anywhere) and it writes
entry.png next to this script's parent directory.
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
PAPER = (247, 243, 232)
INK = (18, 18, 18)
GREY = (90, 86, 76)
ACCENT = (140, 20, 20)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_BOLD = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit `width` pixels."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def draw_block(draw, x, y, width, kicker, headline, summary,
               head_size=30, sum_size=21, head_lines=2):
    """One story: kicker, headline, summary. Returns y below the block."""
    kick_font = SANS_BOLD(17)
    draw.text((x, y), kicker.upper(), font=kick_font, fill=ACCENT)
    y += 23
    head_font = SERIF_BOLD(head_size)
    for line in wrap(draw, headline, head_font, width)[:head_lines]:
        draw.text((x, y), line, font=head_font, fill=INK)
        y += head_size + 5
    y += 1
    sum_font = SANS(sum_size)
    for line in wrap(draw, summary, sum_font, width):
        draw.text((x, y), line, font=sum_font, fill=INK)
        y += sum_size + 5
    return y


def main():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)
    margin = 36
    right = SIZE - margin

    # --- top hairline and issue line -------------------------------------
    draw.line([(margin, 26), (right, 26)], fill=INK, width=2)
    small = SANS(16)
    draw.text((margin, 34), "VOL. I  —  No. 328", font=small, fill=GREY)
    price = "PRICE: ONE DOLLAR"
    draw.text((right - draw.textlength(price, font=small), 34), price,
              font=small, fill=GREY)

    # --- masthead ---------------------------------------------------------
    name = "THE WORLD LEDGER"
    name_font = SERIF_BOLD(66)
    w = draw.textlength(name, font=name_font)
    draw.text(((SIZE - w) / 2, 52), name, font=name_font, fill=INK)

    date_line = "Tuesday, 24 November 2026"
    date_font = SERIF_BOLD(28)
    dw = draw.textlength(date_line, font=date_font)
    draw.text(((SIZE - dw) / 2, 128), date_line, font=date_font, fill=INK)

    # --- double rule under the masthead ----------------------------------
    draw.line([(margin, 166), (right, 166)], fill=INK, width=4)
    draw.line([(margin, 173), (right, 173)], fill=INK, width=1)

    # --- lead story -------------------------------------------------------
    y = 188
    lead_kicker = SANS_BOLD(18)
    draw.text((margin, y), "MARKETS  •  LEAD STORY", font=lead_kicker,
              fill=ACCENT)
    y += 28
    lead_font = SERIF_BOLD(42)
    lead_head = "Nvidia's comeback rally fades\nas shares slide 6%"
    for line in lead_head.split("\n"):
        draw.text((margin, y), line, font=lead_font, fill=INK)
        y += 50
    y += 4
    lead_sum = ("The relief rally around Jensen Huang's return as chief "
                "executive fizzled on Tuesday, with tech stocks stumbling "
                "and the Nasdaq down 1.5%.")
    sum_font = SANS(21)
    for line in wrap(draw, lead_sum, sum_font, right - margin):
        draw.text((margin, y), line, font=sum_font, fill=INK)
        y += 28
    y += 8
    draw.line([(margin, y), (right, y)], fill=INK, width=2)
    y += 14

    # --- story grid: two rows of two, then one full-width story -----------
    col_w = (right - margin - 24) // 2
    left_x = margin
    right_x = margin + col_w + 24

    stories = [
        ("UKRAINE  •  WAR AT SEA",
         "Ukraine calls Libya strike self-defence",
         "Kyiv said on Tuesday its drone attack on Russian ships in Libya "
         "was lawful self-defence, after sinking the corvette Merkury at "
         "Benghazi."),
        ("RUSSIA-UKRAINE WAR",
         "Russian strike on Zaporizhzhia kills two",
         "An overnight Russian attack hit an apartment block, killing two "
         "and wounding 40, including four children, officials said."),
        ("MIDDLE EAST",
         "Israel kills Hamas security chief in Gaza",
         "An Israeli airstrike killed Naeem Abu Nahel, head of Hamas's "
         "internal security apparatus, in Gaza City. At least seven died."),
        ("ECONOMY",
         "US consumer confidence hits near two-year high",
         "The Conference Board index jumped to 103.3 in November, its "
         "highest since January 2025, as Americans grew more upbeat about "
         "jobs and the economy."),
    ]

    row_y = y
    for row in range(2):
        pair = stories[row * 2:(row + 1) * 2]
        end_left = draw_block(draw, left_x, row_y, col_w, *pair[0],
                              head_size=28, sum_size=20)
        end_right = draw_block(draw, right_x, row_y, col_w, *pair[1],
                               head_size=28, sum_size=20)
        row_y = max(end_left, end_right) + 6
        draw.line([(margin, row_y), (right, row_y)], fill=GREY, width=1)
        row_y += 12

    # full-width final story
    row_y = draw_block(draw, margin, row_y, right - margin,
                       "CLIMATE",
                       "COP31 ends without a deal",
                       "The UN climate summit in Antalya closed with no "
                       "agreement — the first such failure since Copenhagen "
                       "in 2009 — split over fossil fuels and finance.",
                       head_size=28, sum_size=20, head_lines=1)

    # --- markets strip (placed below the last story, wherever it ends) ----
    strip_y = row_y + 12
    draw.rectangle([(margin, strip_y), (right, strip_y + 46)],
                   outline=INK, width=2)
    strip_font = SANS_BOLD(20)
    strip = "MARKETS:  Nasdaq -1.5%   •   S&P 500 -0.5%   •   Dow +0.9%   •   Nvidia -6%"
    sw = draw.textlength(strip, font=strip_font)
    draw.text(((SIZE - sw) / 2, strip_y + 12), strip, font=strip_font,
              fill=INK)

    # --- footer ------------------------------------------------------------
    foot_rule_y = strip_y + 46 + 14
    draw.line([(margin, foot_rule_y), (right, foot_rule_y)], fill=INK, width=2)
    foot = ("LONDON — Tuesday, 24 November 2026  •  Compiled from Reuters, "
            "AP, BBC and WSJ reports")
    foot_font = SANS(17)
    fw = draw.textlength(foot, font=foot_font)
    draw.text(((SIZE - fw) / 2, foot_rule_y + 12), foot, font=foot_font,
              fill=GREY)

    out_path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "entry.png")
    img.save(out_path, "PNG")
    print("Wrote", out_path, img.size)


if __name__ == "__main__":
    main()
