import os

import pandas as pd
import streamlit as st

from profile_page import build_profile
from risk_quiz import (
    TABLE_COLUMNS,
    Q5_OPTIONS,
    Q6_OPTIONS,
    Q7_OPTIONS,
    Q8_OPTIONS,
    FEELING_OPTIONS,
    PATIENCE_OPTIONS,
    FALL_ACTION_OPTIONS,
    SELL_OPTIONS,
    score_quiz,
)
from personality import load_items, score_bfi
from functions_fit import fit_all


INVESTORS_FILE = "data/investor_responses.csv"
NEW_CLIENT = "New client"
DEFAULT_INITIAL_WEALTH = 10000000.0
DEFAULT_HORIZON_YEARS = 0.25

SINGLE_QUESTIONS = {
    "q5": Q5_OPTIONS,
    "q6": Q6_OPTIONS,
    "q7": Q7_OPTIONS,
    "q8": Q8_OPTIONS,
    "q16": FEELING_OPTIONS,
    "q17": FEELING_OPTIONS,
    "q20": PATIENCE_OPTIONS,
    "q26": FALL_ACTION_OPTIONS,
    "q27": FALL_ACTION_OPTIONS,
    "q28": SELL_OPTIONS,
}

TABLE_ROWS = {
    "q9": 5,
    "q10": 5,
    "q11": 5,
    "q12": 5,
    "q13": 5,
    "q14": 5,
    "q15": 5,
    "q18": 5,
    "q19": 5,
    "q25": 8,
}


def load_investor_table():
    if not os.path.exists(INVESTORS_FILE):
        return None
    return pd.read_csv(INVESTORS_FILE)


def get_investor_ids():
    table = load_investor_table()
    ids = []
    if table is None:
        return ids
    for investor_id in table["investor_id"]:
        ids.append(investor_id)
    return ids


def text_value(row, column_name):
    value = row[column_name]
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value).strip()


def get_row(investor_id):
    table = load_investor_table()
    matching_rows = table[table["investor_id"] == investor_id]
    return matching_rows.iloc[0]


def build_investor_profile(investor_id, row):
    choices = {}
    for question_number in ["2", "3", "4", "21", "22", "23", "31", "32", "33"]:
        answer = text_value(row, "q" + question_number)
        if answer == "":
            answer = "Not answered"
        choices[question_number] = answer
    q24_scores = []
    for row_number in range(1, 6):
        q24_scores.append(int(text_value(row, "q24_" + str(row_number))))
    exclusions = text_value(row, "q34")
    profile = build_profile(investor_id, choices, q24_scores, DEFAULT_INITIAL_WEALTH, DEFAULT_HORIZON_YEARS, exclusions)
    return profile


def build_quiz_answers(row):
    answers = {}
    for key in SINGLE_QUESTIONS:
        options = SINGLE_QUESTIONS[key]
        answers[key] = options.index(text_value(row, key))
    for key in TABLE_ROWS:
        columns = TABLE_COLUMNS[key]
        choices = []
        for row_number in range(1, TABLE_ROWS[key] + 1):
            choices.append(columns.index(text_value(row, key + "_" + str(row_number))))
        answers[key] = choices
    return answers


def build_bfi_answers(row):
    answers = []
    for item_number in range(1, 16):
        answers.append(int(text_value(row, "bfi_" + str(item_number))))
    return answers


def build_investor(investor_id):
    row = get_row(investor_id)
    profile = build_investor_profile(investor_id, row)
    answers = build_quiz_answers(row)
    results = score_quiz(answers)
    bfi_answers = build_bfi_answers(row)
    traits = score_bfi(load_items(), bfi_answers)
    fits = fit_all(results)
    investor = {
        "profile": profile,
        "answers": answers,
        "results": results,
        "bfi_answers": bfi_answers,
        "traits": traits,
        "fits": fits,
    }
    return investor


def clear_client():
    for key in ["profile", "client_id", "quiz", "personality", "functions"]:
        if key in st.session_state:
            del st.session_state[key]
    old_widget_keys = []
    for key in st.session_state:
        key_text = str(key)
        if key_text.startswith("quiz_") or key_text.startswith("profile_") or key_text.startswith("bfi_"):
            old_widget_keys.append(key)
    for key in old_widget_keys:
        del st.session_state[key]


def load_investor_into_session(investor_id):
    investor = build_investor(investor_id)
    st.session_state["profile"] = investor["profile"]
    st.session_state["client_id"] = investor_id
    st.session_state["quiz"] = {"answers": investor["answers"], "results": investor["results"]}
    st.session_state["personality"] = {"answers": investor["bfi_answers"], "traits": investor["traits"]}
    st.session_state["functions"] = investor["fits"]


def show_investor_picker():
    choices = [NEW_CLIENT]
    for investor_id in get_investor_ids():
        choices.append(investor_id)
    selected = st.sidebar.selectbox("Investor", choices, key="investor_picker")
    if "loaded_investor" not in st.session_state:
        st.session_state["loaded_investor"] = NEW_CLIENT
    if selected != st.session_state["loaded_investor"]:
        clear_client()
        if selected != NEW_CLIENT:
            load_investor_into_session(selected)
        st.session_state["loaded_investor"] = selected
    if selected == NEW_CLIENT:
        st.sidebar.caption("Fill the pages in order for a new client.")
    else:
        st.sidebar.caption("Showing the survey answers of " + selected + ". Names are hidden.")
