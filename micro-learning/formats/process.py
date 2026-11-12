import streamlit as st


def render(slide, layout=None):

    steps = []

    for line in slide["content"].splitlines():

        if "|" not in line:
            continue

        title, content = line.split(
            "|",
            1
        )

        steps.append(
            (title, content)
        )

    cols = st.columns(
        len(steps)
    )

    for idx, step in enumerate(steps):

        with cols[idx]:

            st.markdown(
                f"""
                <div style="
                background:#edf4ff;
                border-radius:16px;
                padding:15px;
                text-align:center;
                min-height:180px;">

                <div style="
                width:40px;
                height:40px;
                margin:auto;
                border-radius:50%;
                background:#306cff;
                color:white;
                line-height:40px;">

                {idx+1}

                </div>

                <h4>{step[0]}</h4>

                <p>{step[1]}</p>

                </div>
                """,
                unsafe_allow_html=True
            )