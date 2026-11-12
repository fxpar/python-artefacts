from pathlib import Path
import json
import re

import streamlit as st
import yaml

from formats import FORMATS




CONTENT_DIR = Path("content")
TEMPLATE_DIR = Path("templates")


# ------------------------
# templates
# ------------------------

def get_dialogue_layouts():

    file = TEMPLATE_DIR / "dialogue.json"

    with open(
        file,
        encoding="utf8"
    ) as f:

        data = json.load(f)

    return data["layouts"]


# ------------------------
# parser markdown
# ------------------------

def parse_slides(text):

    blocks = re.findall(
        r"(---[\s\S]*?---[\s\S]*?)(?=\n---|\Z)",
        text
    )

    slides = []

    for block in blocks:

        match = re.match(
            r"---\n(.*?)\n---",
            block,
            re.DOTALL
        )

        if not match:
            continue

        meta = yaml.safe_load(
            match.group(1)
        )

        content = block[
            match.end():
        ].strip()

        slides.append(
            {
                "meta": meta,
                "content": content
            }
        )

    return slides


# ------------------------
# session
# ------------------------

if "slide_index" not in st.session_state:
    st.session_state.slide_index = 0


# ------------------------
# ui
# ------------------------

st.set_page_config(
    layout="wide"
)

st.title(
    "MicroLearning Builder"
)


course_files = sorted(
    CONTENT_DIR.glob("*.md")
)

course_names = [
    f.name
    for f in course_files
]

selected_course = st.sidebar.selectbox(
    "Cours",
    course_names
)

course_file = (
    CONTENT_DIR /
    selected_course
)

source_text = course_file.read_text(
    encoding="utf8"
)

layouts = get_dialogue_layouts()

selected_layout = st.sidebar.selectbox(
    "Layout",
    layouts
)


editor_col, preview_col = st.columns(
    [1, 1]
)


with editor_col:

    st.subheader(
        "Markdown"
    )

    edited_text = st.text_area(
        "",
        value=source_text,
        height=1000
    )

    save_col1, save_col2 = st.columns(2)

    with save_col1:

        if st.button(
            "💾 Sauvegarder"
        ):

            course_file.write_text(
                edited_text,
                encoding="utf8"
            )

            st.success(
                "Sauvegardé"
            )

    slides = parse_slides(
        edited_text
    )
    
    if st.button("📦 Export HTML"):

        preview_dir = Path("preview")
        preview_dir.mkdir(exist_ok=True)

        course_name = course_file.stem

        html_file = (
            preview_dir /
            f"{course_name}.html"
        )

        slides_html = []

        for i, slide in enumerate(slides):

            slide_type = slide["meta"].get(
                "type"
            )

            renderer = FORMATS.get(
                slide_type
            )

            if (
                renderer
                and hasattr(
                    renderer,
                    "render_html"
                )
            ):

                slide_content = (
                    renderer.render_html(
                        slide
                    )
                )

            else:

                slide_content = (
                    slide["content"]
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br>")
                )

            slides_html.append(
                f"""
                <section class="slide">

                    {slide_content}

                </section>
                """
            )

        final_html = f"""
    <!DOCTYPE html>

    <html>

    <head>

    <meta charset="utf-8">

    <title>{course_name}</title>

    <style>

    body {{
        margin:0;
        font-family:Segoe UI,sans-serif;
        background:#f5f5f5;
    }}

    .slide {{

        display:none;

        padding:40px;

        max-width:1200px;

        margin:auto;
    }}

    .slide.active {{
        display:block;
    }}

    .navigation {{

        position:fixed;

        bottom:20px;

        left:0;

        right:0;

        text-align:center;
    }}

    button {{

        padding:12px 20px;

        margin:10px;

        cursor:pointer;
    }}

    </style>

    </head>

    <body>

    {''.join(slides_html)}

    <div class="navigation">

    <button onclick="prevSlide()">

    ◀

    </button>

    <button onclick="nextSlide()">

    ▶

    </button>

    </div>

    <script>

    let current = 0;

    const slides =
    document.querySelectorAll(
    '.slide'
    );

    function show(index){{

        slides.forEach(
            s=>s.classList.remove(
                'active'
            )
        );

        slides[index]
        .classList.add(
            'active'
        );
    }}

    function nextSlide(){{

        if(
            current <
            slides.length-1
        )
        {{

            current++;

            show(current);
        }}
    }}

    function prevSlide(){{

        if(
            current > 0
        )
        {{

            current--;

            show(current);
        }}
    }}

    document.addEventListener(
        "keydown",
        function(e)
        {{

            if(
                e.key === "ArrowRight"
            )
            {{
                nextSlide();
            }}

            if(
                e.key === "ArrowLeft"
            )
            {{
                prevSlide();
            }}
        }}
    );

    show(0);

    </script>

    </body>

    </html>
    """

        html_file.write_text(
            final_html,
            encoding="utf8"
        )

        st.success(
            f"Exporté : {html_file}"
        )


with preview_col:

    st.subheader(
        "Preview"
    )

    nav1, nav2, nav3 = st.columns(
        [1, 2, 1]
    )

    with nav1:

        if st.button(
            "◀"
        ):

            if (
                st.session_state.slide_index
                > 0
            ):

                st.session_state.slide_index -= 1

    with nav3:

        if st.button(
            "▶"
        ):

            if (
                st.session_state.slide_index
                < len(slides) - 1
            ):

                st.session_state.slide_index += 1

    current = (
        st.session_state.slide_index
    )

    st.caption(
        f"Slide {current+1}/{len(slides)}"
    )

    if slides:

        slide = slides[current]

        slide_type = slide[
            "meta"
        ].get(
            "type"
        )

        renderer = FORMATS.get(
            slide_type
        )

        if renderer:

            renderer.render(
                slide,
                selected_layout
            )

        else:

            st.warning(
                f"Type non géré : {slide_type}"
            )
