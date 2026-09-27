import streamlit as st

from profile_page import show_profile_page
from risk_quiz import show_risk_quiz_page
from personality import show_personality_page
from functions_fit import show_functions_page
from portfolio import show_portfolio_page
from advice import show_advice_page
from how_it_works import show_how_it_works_page
from group_results import show_group_results_page
from investors import show_investor_picker


st.set_page_config(page_title="Robo-Advisor Portal", layout="wide")

questionnaire_pages = [
    st.Page(show_profile_page, title="Client Profile", icon=":material/person:", url_path="profile", default=True),
    st.Page(show_risk_quiz_page, title="Risk & Time Quiz", icon=":material/casino:", url_path="quiz"),
    st.Page(show_personality_page, title="Personality", icon=":material/psychology:", url_path="personality"),
]

results_pages = [
    st.Page(show_functions_page, title="My Utility & Value", icon=":material/show_chart:", url_path="utility"),
    st.Page(show_portfolio_page, title="My Portfolios", icon=":material/pie_chart:", url_path="portfolios"),
    st.Page(show_advice_page, title="Advice", icon=":material/lightbulb:", url_path="advice"),
]

report_pages = [
    st.Page(show_group_results_page, title="Group Results", icon=":material/groups:", url_path="group"),
]

help_pages = [
    st.Page(show_how_it_works_page, title="How It Works", icon=":material/help:", url_path="how-it-works"),
]

sections = {
    "Questionnaire": questionnaire_pages,
    "My Results": results_pages,
    "Reports": report_pages,
    "Help": help_pages,
}

page = st.navigation(sections, position="hidden")

show_investor_picker()
st.sidebar.divider()

for section_name in sections:
    st.sidebar.caption(section_name)
    for section_page in sections[section_name]:
        st.sidebar.page_link(section_page)

page.run()
