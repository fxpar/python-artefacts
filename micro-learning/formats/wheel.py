import json
import streamlit as st
import streamlit.components.v1 as components


def build_html(slide):

    center = slide["meta"].get(
        "center",
        "Centre"
    )

    items = []

    for line in slide["content"].splitlines():

        line = line.strip()

        if "|" not in line:
            continue

        title, content = line.split(
            "|",
            1
        )

        items.append({
            "title": title.strip(),
            "content": content.strip()
        })

    items_json = json.dumps(items)

    return f"""
<div class="wheel-wrapper">

<div id="wheel-container"></div>

<div id="wheel-info">
Cliquez sur un élément.
</div>

<style>

.wheel-wrapper {{
    font-family:Segoe UI,sans-serif;
}}

#wheel-info {{
    margin-top:20px;
    padding:15px;
    border-radius:12px;
    background:#f5f8ff;
    min-height:120px;
}}

.node {{
    fill:#dbe9ff;
    stroke:#306cff;
    stroke-width:2;
    cursor:pointer;
}}

.node:hover {{
    fill:#9bc0ff;
}}

.node-label {{
    font-size:12px;
    font-weight:bold;
    text-anchor:middle;
    dominant-baseline:middle;
    pointer-events:none;
}}

.center-circle {{
    fill:#306cff;
}}

.center-label {{
    fill:white;
    font-size:20px;
    font-weight:bold;
    text-anchor:middle;
}}

</style>

<script>

(function(){{

const items = {items_json};

let html = `
<svg
viewBox="0 0 700 700"
width="100%"
height="600">

<circle
class="center-circle"
cx="350"
cy="350"
r="90">
</circle>

<text
class="center-label"
x="350"
y="358">
{center}
</text>
`;

const radius = 220;

items.forEach(
(item,index)=>{{

    const angle =
    (index/items.length)
    * Math.PI * 2
    - Math.PI/2;

    const x =
    350 +
    Math.cos(angle)
    * radius;

    const y =
    350 +
    Math.sin(angle)
    * radius;

    html += `

    <g>

        <circle
        class="node"
        cx="${{x}}"
        cy="${{y}}"
        r="60"
        data-title="${{item.title}}"
        data-content="${{item.content}}">
        </circle>

        <text
        class="node-label"
        x="${{x}}"
        y="${{y}}">
        ${{item.title}}
        </text>

    </g>

    `;

}});

html += "</svg>";

document
.getElementById(
    "wheel-container"
)
.innerHTML = html;

document
.querySelectorAll(
    ".node"
)
.forEach(node => {{

    node.addEventListener(
        "click",
        function() {{

            document
            .getElementById(
                "wheel-info"
            )
            .innerHTML =

            "<h3>" +
            this.dataset.title +
            "</h3><p>" +
            this.dataset.content +
            "</p>";

        }}
    );

}});

}})();

</script>

</div>
"""


def render(slide, layout=None):

    html = build_html(slide)

    components.html(
        html,
        height=750,
        scrolling=False
    )


def render_html(slide):

    return build_html(slide)