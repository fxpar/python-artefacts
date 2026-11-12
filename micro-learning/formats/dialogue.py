from pathlib import Path
import re

import streamlit.components.v1 as components


ASSETS_DIR = Path("assets")


# --------------------------------------------------
# Illustrations
# --------------------------------------------------

def get_available_illustrations():

    items = []

    for svg in sorted(
        ASSETS_DIR.glob("*.svg")
    ):

        name = svg.stem

        if name.startswith(
            "undraw_"
        ):
            name = name[7:]

        name = re.sub(
            r"_[a-zA-Z0-9]{4}$",
            "",
            name
        )

        items.append(
            {
                "label": name,
                "file": svg
            }
        )

    return items


def find_illustration(slide):

    illustration = slide[
        "meta"
    ].get(
        "illustration"
    )

    if illustration:

        for svg in ASSETS_DIR.glob(
            "*.svg"
        ):

            if illustration in svg.name:
                return svg

    illustrations = (
        get_available_illustrations()
    )

    if illustrations:
        return illustrations[0]["file"]

    return None


# --------------------------------------------------
# Hotspots
# --------------------------------------------------

def parse_hotspots(text):

    lines = text.splitlines()

    intro = []

    hotspots = []

    current = None

    mode = "intro"

    for line in lines:

        clean = line.strip()

        if clean.startswith("++"):

            mode = "hotspot"

            if current:
                hotspots.append(
                    current
                )

            current = {
                "title": clean[2:].strip(),
                "body": []
            }

            continue

        if mode == "intro":

            if clean:
                intro.append(clean)

        else:

            if current and clean:

                current["body"].append(
                    clean
                )

    if current:
        hotspots.append(current)

    return (
        "\n\n".join(intro),
        hotspots
    )


# --------------------------------------------------
# HTML builder
# --------------------------------------------------

def build_html(
    slide,
    layout="left"
):

    speaker = slide[
        "meta"
    ].get(
        "speaker",
        "Personnage"
    )

    intro, hotspots = (
        parse_hotspots(
            slide["content"]
        )
    )

    illustration = (
        find_illustration(
            slide
        )
    )

    image_html = ""

    if illustration:

        svg_content = (
            illustration
            .read_text(
                encoding="utf8"
            )
        )

        image_html = f"""
        <div class="dialogue-image">
            {svg_content}
        </div>
        """

    if layout == "right":

        body_html = f"""

        <div class="dialogue-row">

            <div class="dialogue-bubble">

                <div class="dialogue-speaker">
                    {speaker}
                </div>

                <div class="dialogue-text">
                    {intro}
                </div>

            </div>

            {image_html}

        </div>
        """

    elif layout == "card":

        body_html = f"""

        <div class="dialogue-card">

            {image_html}

            <div class="dialogue-speaker">
                {speaker}
            </div>

            <div class="dialogue-text">
                {intro}
            </div>

        </div>
        """

    else:

        body_html = f"""

        <div class="dialogue-row">

            {image_html}

            <div class="dialogue-bubble">

                <div class="dialogue-speaker">
                    {speaker}
                </div>

                <div class="dialogue-text">
                    {intro}
                </div>

            </div>

        </div>
        """

    hotspots_html = ""

    for hotspot in hotspots:

        body = "<br>".join(
            hotspot["body"]
        )

        hotspots_html += f"""

        <details class="dialogue-hotspot">

            <summary>
                + {hotspot["title"]}
            </summary>

            <div class="dialogue-hotspot-content">

                {body}

            </div>

        </details>
        """

    return f"""

    <div class="dialogue">

        <style>

        .dialogue {{
            font-family: Segoe UI, sans-serif;
        }}

        .dialogue-row {{
            display:flex;
            gap:20px;
            align-items:flex-start;
            margin-bottom:15px;
        }}

        .dialogue-image {{
            width:220px;
            max-width:220px;
            flex-shrink:0;
        }}

        .dialogue-image svg {{
            width:100%;
            height:auto;
        }}

        .dialogue-bubble {{

            flex:1;

            background:#edf4ff;

            border-radius:20px;

            padding:20px;
        }}

        .dialogue-card {{

            border:1px solid #dddddd;

            border-radius:20px;

            padding:25px;

            background:white;
        }}

        .dialogue-speaker {{

            font-size:1.1rem;

            font-weight:bold;

            margin-bottom:10px;
        }}

        .dialogue-text {{

            line-height:1.6;
        }}

        .dialogue-hotspot {{

            margin-top:12px;

            border:1px solid #d5e2ff;

            border-radius:10px;

            background:#f8fbff;

            padding:10px;
        }}

        .dialogue-hotspot summary {{

            cursor:pointer;

            font-weight:bold;
        }}

        .dialogue-hotspot-content {{

            margin-top:10px;
        }}

        </style>

        {body_html}

        {hotspots_html}

    </div>
    """


# --------------------------------------------------
# Streamlit preview
# --------------------------------------------------

def render(
    slide,
    layout="left"
):

    html = build_html(
        slide,
        layout
    )

    components.html(
        html,
        height=800,
        scrolling=True
    )


# --------------------------------------------------
# Export HTML
# --------------------------------------------------

def render_html(
    slide,
    layout="left"
):

    return build_html(
        slide,
        layout
    )