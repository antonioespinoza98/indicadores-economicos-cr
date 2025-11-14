import streamlit as st
from st_pages import add_page_title, get_nav_from_toml


st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed")


nav = get_nav_from_toml(".streamlit/pages.toml")

st.logo("./docs/img/logo.png", size="large")

pg = st.navigation(nav)

add_page_title(pg)

pg.run()