import streamlit as st


def render(slide, layout=None):

    items = []

    for line in slide["content"].splitlines():

        if "|" not in line:
            continue

        items.append(
            line.split("|",1)
        )

    items.reverse()

    width = 100

    for i,item in enumerate(items):

        current = width - (i * 15)

        st.markdown(
            f"""
            <div style="
                width:{current}%;
                margin:auto;
                margin-top:6px;
                background:#dbe9ff;
                padding:15px;
                text-align:center;
                border-radius:8px;
            ">

                <strong>
                    {item[0]}
                </strong>

                <br>

                {item[1]}

            </div>
            """,
            unsafe_allow_html=True
        )