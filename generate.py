#!/usr/bin/env python3
"""Render the one-image summary of Monday 23 November 2026.

The picture is drawn from scratch with Pillow: a newspaper-style
masthead naming the day, six story panels (climate, Gulf conflict,
Ukraine, the Baltic, Seoul, the UN) and an "also today" strip with
five shorter items. Every headline below was checked against the
morning wires and roundups of 23 November 2026 before drawing.

Usage: python3 generate.py  (writes entry.png next to this file)
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

CANVAS = 1024
CREAM = (247, 243, 232)
INK = (18, 18, 20)
CARD = (255, 255, 255)
GREY = (84, 84, 88)
NAVY = (16, 24, 48)
GOLD = (255, 209, 64)
RED = (232, 64, 52)
EDGE = (215, 208, 190)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(bold, size):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def fit_text(draw, text, bold, size, limit):
    """Largest size at or below `size` that fits `limit` pixels wide."""
    while size > 16:
        font = load_font(bold, size)
        if draw.textlength(text, font=font) <= limit:
            return font
        size -= 1
    return load_font(bold, size)


def story_panel(draw, box, accent, kicker, headline, body):
    """One white card: coloured top bar, kicker, headline, body copy."""
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=14, fill=CARD, outline=EDGE, width=2)
    draw.rectangle([x0, y0, x1, y0 + 10], fill=accent)
    draw.text((x0 + 20, y0 + 24), kicker, font=load_font(True, 17), fill=accent)
    cursor = y0 + 52
    for line in textwrap.wrap(headline, width=24):
        font = fit_text(draw, line, True, 27, (x1 - x0) - 40)
        draw.text((x0 + 20, cursor), line, font=font, fill=INK)
        cursor += 32
    cursor += 4
    lines = textwrap.wrap(body, width=39)
    size = 19
    # Shrink the body copy if it would run past the card's bottom edge.
    while size > 14 and cursor + len(lines) * (size + 5) > y1 - 10:
        size -= 1
    for line in lines:
        draw.text((x0 + 20, cursor), line, font=load_font(False, size), fill=GREY)
        cursor += size + 5


def brief_strip(draw, box, items):
    """Dark strip listing the shorter stories of the day."""
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=14, fill=NAVY)
    draw.text((x0 + 20, y0 + 14), "ALSO TODAY", font=load_font(True, 22), fill=GOLD)
    cursor = y0 + 50
    for item in items:
        text = "•  " + item
        font = fit_text(draw, text, True, 17, (x1 - x0) - 40)
        draw.text((x0 + 20, cursor), text, font=font, fill=(240, 243, 250))
        cursor += 27


def main():
    img = Image.new("RGB", (CANVAS, CANVAS), CREAM)
    draw = ImageDraw.Draw(img)

    # Masthead: paper name, red rule, the date in gold.
    draw.rectangle([0, 0, CANVAS, 150], fill=NAVY)
    draw.text((36, 18), "THE WORLD IN ONE DAY",
              font=load_font(True, 52), fill=(255, 255, 255))
    draw.rectangle([36, 86, 988, 90], fill=RED)
    draw.text((36, 100), "MONDAY  23 NOVEMBER 2026",
              font=load_font(True, 34), fill=GOLD)
    draw.text((988, 100), "ONE IMAGE  •  THE DAY'S NEWS",
              font=load_font(True, 20), fill=(210, 218, 235), anchor="ra")

    stories = [
        dict(accent=(22, 138, 90), kicker="CLIMATE  •  ANTALYA, TURKIYE",
             headline="COP31 TALKS COLLAPSE",
             body="Climate summit ends with NO DEAL. EU rejects final draft "
                  "that left out fossil fuels."),
        dict(accent=(200, 52, 40), kicker="CONFLICT  •  BAHRAIN / HORMUZ",
             headline="IRAN STRIKES BAHRAIN",
             body="Projectiles hit a Sitra industrial site, 2 injured. "
                  "Tankers set ablaze in the Strait."),
        dict(accent=(52, 92, 180), kicker="WAR  •  DYMER, UKRAINE",
             headline="DRONE HITS APARTMENTS",
             body="Russian drone hits a five-storey block near Kyiv. "
                  "2 killed, at least 14 people missing."),
        dict(accent=(128, 70, 170), kicker="BALTIC SEA  •  OFF FINLAND",
             headline="RUSSIAN SHIP ABLAZE",
             body="Cargo ship still burning off Finland after a drone "
                  "attack in the Baltic Sea."),
        dict(accent=(176, 120, 20), kicker="ASIA  •  SEOUL, SOUTH KOREA",
             headline="MINISTER QUITS OVER AI CHEATING",
             body="Education minister resigns over AI cheating chaos "
                  "in the college exam."),
        dict(accent=(10, 130, 140), kicker="DIPLOMACY  •  UNITED NATIONS",
             headline="TALKS ON KILLER ROBOTS GO ON",
             body="Nations agree to keep negotiating curbs on lethal "
                  "autonomous weapons."),
    ]

    margin, gap = 36, 20
    width = (CANVAS - 2 * margin - gap) // 2
    height = 178
    top = 172
    for i, story in enumerate(stories):
        x = margin + (i % 2) * (width + gap)
        y = top + (i // 2) * (height + gap)
        story_panel(draw, (x, y, x + width, y + height), **story)

    briefs = [
        "INDONESIA: 24 bodies recovered after a factory fire; search goes on for the missing.",
        "INDIA: Nepal PM Balendra Shah holds talks with PM Modi on a state visit to New Delhi.",
        "CRICKET: India post a record 720/9 declared in the Wellington Test vs New Zealand.",
        "PORTUGAL: Thousands march in Lisbon as living costs fuel anger.",
        "SOUTH SUDAN: 24 civilians killed in fresh violence, officials say.",
    ]
    strip_top = top + 3 * (height + gap) + 2
    brief_strip(draw, (margin, strip_top, CANVAS - margin, 962), briefs)

    draw.text((CANVAS // 2, 982),
              "The day's biggest stories, across every region - in a single picture.",
              font=load_font(False, 18), fill=GREY, anchor="ma")

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
