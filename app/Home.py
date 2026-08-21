import streamlit as st

st.set_page_config(
    page_title="Machine Learning Operations",
    layout="wide"
)


# Define the project pages
job_predictor_page = st.Page(
    "pages/XiaoYao_Jobs_Predictor.py",
    title="Job Prediction",
)

health_predictor_page = st.Page(
    "pages/Damien_Health_Predictor.py",
    title="Health Prediction",
)


# Navigation
page = st.navigation(
    [
        job_predictor_page,
        health_predictor_page
    ],
    position="sidebar"
)


page.run()