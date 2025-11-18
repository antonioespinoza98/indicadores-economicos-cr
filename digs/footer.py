import streamlit as st
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

import base64

def load_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { margin-bottom: 180px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="#009EDB",
        padding=px(10, 0, 10, 0),
        text_align="center",
        height="auto",
        opacity=1,
        box_shadow="0 -1px 3px rgba(0,0,0,0.1)"
    )

    body = p()
    foot = div(style=style_div)(body)

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    img_b64 = load_image_base64("./docs/img/logo.svg")
    img_tag = image(
        f"data:image/svg+xml;base64,{img_b64}",
        width=px(180),
        height=px(60)
    )

    myargs = [
        "Aplicación desarrollada por ",
        img_tag,
        br(),
        " Versión experimental 0.0.1"
    ]
    layout(*myargs)


if __name__ == "__main__":
    footer()