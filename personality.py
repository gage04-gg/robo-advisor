import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from profile_page import update_response_row, widget_key


ITEMS_FILE = "data/bfi2_items.csv"

NUMBER_OF_ITEMS = 15
LAST_ITEM_IN_Q29 = 8

TRAITS = [
    "Extraversion",
    "Agreeableness",
    "Conscientiousness",
    "Negative Emotionality",
    "Open-Mindedness",
]

LIKERT_OPTIONS = ["1", "2", "3", "4", "5"]


def load_items():
    items = pd.read_csv(ITEMS_FILE)
    return items


def get_saved_answers():
    if "personality" in st.session_state:
        return st.session_state["personality"]["answers"]
    return None


def ask_one_item(items, i, saved_answers):
    item_number = int(items.loc[i, "item_number"])
    start_index = None
    if saved_answers is not None:
        start_index = saved_answers[i] - 1
    answer = st.radio(
        items.loc[i, "item_text"],
        LIKERT_OPTIONS,
        index=start_index,
        horizontal=True,
        key=widget_key("bfi_" + str(item_number)),
    )
    if answer is None:
        return None
    return int(answer)


def ask_items(items):
    saved_answers = get_saved_answers()
    answers = []
    st.markdown("**29. I am someone who...**")
    st.caption("1 is strongly disagree, 5 is strongly agree.")
    for i in range(LAST_ITEM_IN_Q29):
        answers.append(ask_one_item(items, i, saved_answers))
    st.markdown("**30. I am someone who...**")
    st.caption("Continued. 1 is strongly disagree, 5 is strongly agree.")
    for i in range(LAST_ITEM_IN_Q29, len(items)):
        answers.append(ask_one_item(items, i, saved_answers))
    return answers


def read_typed_answers(typed_text):
    cleaned_text = typed_text.replace(",", " ")
    cleaned_text = cleaned_text.replace("\n", " ")
    parts = cleaned_text.split()
    answers = []
    for part in parts:
        if part not in LIKERT_OPTIONS:
            return None, "'" + part + "' is not a number from 1 to 5."
        answers.append(int(part))
    if len(answers) != NUMBER_OF_ITEMS:
        return None, "You typed " + str(len(answers)) + " answers, but there must be exactly " + str(NUMBER_OF_ITEMS) + "."
    return answers, ""


def score_item(answer, is_reversed):
    if is_reversed == "yes":
        return 6 - answer
    return answer


def score_bfi(items, answers):
    totals = {}
    counts = {}
    for trait in TRAITS:
        totals[trait] = 0
        counts[trait] = 0
    for i in range(len(items)):
        trait = items.loc[i, "trait"]
        totals[trait] = totals[trait] + score_item(answers[i], items.loc[i, "reverse"])
        counts[trait] = counts[trait] + 1
    trait_scores = {}
    for trait in TRAITS:
        trait_scores[trait] = totals[trait] / counts[trait]
    return trait_scores


def level_text(score):
    if score >= 3.5:
        return "High"
    if score <= 2.5:
        return "Low"
    return "Medium"


def make_trait_table(trait_scores):
    scores = []
    levels = []
    for trait in TRAITS:
        scores.append(round(trait_scores[trait], 2))
        levels.append(level_text(trait_scores[trait]))
    return pd.DataFrame({"Trait": TRAITS, "Score (1 to 5)": scores, "Level": levels})


def make_item_table(items, answers):
    numbers = []
    texts = []
    traits = []
    given = []
    scored = []
    for i in range(len(items)):
        numbers.append(int(items.loc[i, "item_number"]))
        texts.append(items.loc[i, "item_text"])
        traits.append(items.loc[i, "trait"])
        given.append(answers[i])
        scored.append(score_item(answers[i], items.loc[i, "reverse"]))
    table = pd.DataFrame(
        {
            "Item": numbers,
            "I am someone who...": texts,
            "Trait": traits,
            "Answer": given,
            "Score used": scored,
        }
    )
    return table


def make_radar_chart(trait_scores):
    number_of_traits = len(TRAITS)
    angles = []
    values = []
    for i in range(number_of_traits):
        angles.append(2 * np.pi * i / number_of_traits)
        values.append(trait_scores[TRAITS[i]])
    angles.append(angles[0])
    values.append(values[0])

    figure = plt.figure(figsize=(5, 5))
    axis = figure.add_subplot(111, polar=True)
    axis.plot(angles, values, color="tab:blue", linewidth=2)
    axis.fill(angles, values, color="tab:blue", alpha=0.25)
    axis.set_xticks(angles[:-1])
    axis.set_xticklabels(TRAITS, fontsize=9)
    axis.set_ylim(0, 5)
    axis.set_yticks([1, 2, 3, 4, 5])
    axis.set_title("Big Five personality profile", pad=20)
    figure.tight_layout()
    return figure


def save_personality(answers, trait_scores):
    st.session_state["personality"] = {"answers": answers, "traits": trait_scores}
    if "client_id" in st.session_state:
        values = {}
        for trait in TRAITS:
            values["bfi_" + trait] = trait_scores[trait]
        answer_text = ""
        for answer in answers:
            answer_text = answer_text + str(answer)
        values["raw_bfi"] = answer_text
        update_response_row(st.session_state["client_id"], values)


def show_results(items):
    answers = st.session_state["personality"]["answers"]
    trait_scores = st.session_state["personality"]["traits"]
    st.subheader("Your personality scores")
    left_column, right_column = st.columns(2)
    with left_column:
        st.table(make_trait_table(trait_scores))
        st.caption("Each trait is the average of its 3 items after reverse scoring. High means 3.5 or more. Low means 2.5 or less.")
    with right_column:
        figure = make_radar_chart(trait_scores)
        st.pyplot(figure)
        plt.close(figure)
    with st.expander("See how each item was scored"):
        st.table(make_item_table(items, answers))
        st.caption("Reverse-keyed items are scored as 6 minus the answer.")


def answer_on_screen(items):
    with st.form(widget_key("bfi_form")):
        answers = ask_items(items)
        submitted = st.form_submit_button("Submit answers")
    if not submitted:
        return None
    for answer in answers:
        if answer is None:
            st.error("Please answer all " + str(NUMBER_OF_ITEMS) + " statements.")
            return None
    return answers


def answer_by_typing():
    with st.form(widget_key("bfi_typed_form")):
        st.write("Type the 15 answers in item order (Q29 rows 1 to 8, then Q30 rows 1 to 7), separated by spaces or commas.")
        typed_text = st.text_area("Answers", height=80)
        submitted = st.form_submit_button("Submit answers")
    if not submitted:
        return None
    answers, error_message = read_typed_answers(typed_text)
    if answers is None:
        st.error(error_message)
    return answers


def show_personality_page():
    st.title("Personality")
    st.subheader("A few things about you")
    st.write('Each statement completes the sentence "I am someone who...". There are no right answers. Answer quickly, your first reaction is usually best.')
    st.caption("Big Five Inventory-2 Extra-Short Form (BFI-2-XS). BFI-2 items copyright 2015 by Oliver P. John and Christopher J. Soto. Soto & John (2017), Journal of Research in Personality, 68, 69-81.")
    if "profile" not in st.session_state:
        st.warning("Please fill the Client Profile first, so your answers can be saved.")

    items = load_items()
    input_method = st.radio("How do you want to enter the answers?", ["Answer on screen", "Type all 15 answers"], horizontal=True)
    if input_method == "Answer on screen":
        answers = answer_on_screen(items)
    else:
        answers = answer_by_typing()

    if answers is not None:
        trait_scores = score_bfi(items, answers)
        save_personality(answers, trait_scores)
        st.success("Personality answers saved.")

    if "personality" in st.session_state:
        show_results(items)
