import os
from datetime import datetime

import pandas as pd
import streamlit as st


RESPONSES_FILE = "data/responses.csv"

EXPERIENCE_OPTIONS = ["None", "Under a year", "1-3 years", "More than 3 years"]
MARKETS_OPTIONS = ["Never", "Occasionally", "Frequently", "Daily"]
PREFERRED_HORIZON_OPTIONS = ["Under a year", "1-3 years", "3-5 years", "More than 5 years"]

FAILURE_OPTIONS = [
    "Rs 10,00,000, I cannot accept any loss",
    "Rs 9,50,000, a loss of up to 5%",
    "Rs 9,00,000, a loss of up to 10%",
    "Rs 8,00,000, a loss of up to 20%",
    "Below Rs 8,00,000 is still acceptable",
]
FAILURE_LOSSES = [0.0, 0.05, 0.10, 0.20, 0.30]

SAFE_OPTIONS = ["None of it", "About a quarter", "About half", "About three quarters", "Almost all of it"]
SAFE_SHARES = [0.0, 0.25, 0.50, 0.75, 0.90]

SUCCESS_OPTIONS = [
    "Rs 10,50,000, a 5% return",
    "Rs 11,00,000, a 10% return",
    "Rs 12,00,000, a 20% return",
    "Rs 13,00,000, a 30% return",
    "Rs 15,00,000 or more",
]
SUCCESS_RETURNS = [0.05, 0.10, 0.20, 0.30, 0.50]

Q24_STATEMENTS = [
    "I first think about what I could lose.",
    "I first think about how much it could grow.",
    "I prefer a near-certain small gain to an uncertain large one.",
    "I keep my money in separate buckets by purpose.",
    "I would hold one small bet beside a safe portfolio.",
]
Q24_LABELS = ["Loss focus", "Gain focus", "Certainty preference", "Mental accounting", "Layered (BPT) thinking"]

FALL_OPTIONS = ["Under 10%", "10-20%", "20-30%", "More than 30%"]
STOCK_COUNT_OPTIONS = ["Under 5", "5-15", "15-30", "More than 30", "No preference"]
APPROACH_OPTIONS = [
    "Preserve capital above everything else",
    "Balance risk and return",
    "Prioritise long-term growth",
    "Pursue high-risk, high-return opportunities",
]

LIKERT_OPTIONS = ["1", "2", "3", "4", "5"]


def format_rupees(amount):
    whole = int(round(amount))
    sign = ""
    if whole < 0:
        sign = "-"
        whole = -whole
    digits = str(whole)
    if len(digits) <= 3:
        return sign + "Rs " + digits
    last_three = digits[-3:]
    rest = digits[:-3]
    groups = []
    while len(rest) > 2:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest != "":
        groups.insert(0, rest)
    return sign + "Rs " + ",".join(groups) + "," + last_three


def add_new_response_row(values):
    new_row = pd.DataFrame([values])
    if os.path.exists(RESPONSES_FILE):
        old_rows = pd.read_csv(RESPONSES_FILE, dtype={"client_id": str})
        all_rows = pd.concat([old_rows, new_row], ignore_index=True)
    else:
        all_rows = new_row
    all_rows.to_csv(RESPONSES_FILE, index=False)


def update_response_row(client_id, values):
    if not os.path.exists(RESPONSES_FILE):
        return False
    all_rows = pd.read_csv(RESPONSES_FILE, dtype={"client_id": str})
    matching_rows = all_rows["client_id"] == client_id
    if matching_rows.sum() == 0:
        return False
    new_columns = []
    for column_name in values:
        if column_name not in all_rows.columns:
            new_columns.append(column_name)
    if len(new_columns) > 0:
        empty_columns = pd.DataFrame(index=all_rows.index, columns=new_columns)
        all_rows = pd.concat([all_rows, empty_columns], axis=1)
    for column_name in values:
        all_rows[column_name] = all_rows[column_name].astype(object)
        all_rows.loc[matching_rows, column_name] = values[column_name]
    all_rows.to_csv(RESPONSES_FILE, index=False)
    return True


def widget_key(name):
    version = 0
    if "answers_version" in st.session_state:
        version = st.session_state["answers_version"]
    return name + "_v" + str(version)


def get_saved_value(key, default_value):
    if "profile" in st.session_state:
        return st.session_state["profile"][key]
    return default_value


def get_saved_index(key, options):
    if "profile" in st.session_state:
        saved_answer = st.session_state["profile"][key]
        if saved_answer in options:
            return options.index(saved_answer)
    return None


def ask_profile_choice(key, question, options):
    answer = st.radio(question, options, index=get_saved_index(key, options), key=widget_key("profile_" + key))
    return answer


def ask_q24():
    st.markdown("**24. How much do you agree with each statement?**")
    st.caption("1 is strongly disagree, 5 is strongly agree.")
    saved_scores = get_saved_value("q24_scores", None)
    scores = []
    for i in range(len(Q24_STATEMENTS)):
        start_index = None
        if saved_scores is not None:
            start_index = saved_scores[i] - 1
        answer = st.radio(Q24_STATEMENTS[i], LIKERT_OPTIONS, index=start_index, horizontal=True, key=widget_key("profile_q24_" + str(i)))
        if answer is None:
            scores.append(None)
        else:
            scores.append(int(answer))
    return scores


def compute_security_level(initial_wealth, failure_answer):
    loss = FAILURE_LOSSES[FAILURE_OPTIONS.index(failure_answer)]
    security_level = initial_wealth * (1 - loss)
    return loss, security_level


def compute_aspiration_level(initial_wealth, horizon_years, success_answer):
    yearly_return = SUCCESS_RETURNS[SUCCESS_OPTIONS.index(success_answer)]
    aspiration_level = initial_wealth * (1 + yearly_return) ** horizon_years
    return yearly_return, aspiration_level


def find_missing_answers(name, choices, q24_scores):
    missing = []
    if name.strip() == "":
        missing.append("1")
    for question_number in choices:
        if choices[question_number] is None:
            missing.append(question_number)
    for score in q24_scores:
        if score is None:
            missing.append("24")
            break
    return missing


def build_profile(name, choices, q24_scores, initial_wealth, horizon_years, exclusions):
    security_loss, security_level = compute_security_level(initial_wealth, choices["21"])
    aspiration_return, aspiration_level = compute_aspiration_level(initial_wealth, horizon_years, choices["23"])
    safe_share = SAFE_SHARES[SAFE_OPTIONS.index(choices["22"])]
    profile = {
        "name": name.strip(),
        "experience": choices["2"],
        "follows_markets": choices["3"],
        "preferred_horizon": choices["4"],
        "initial_wealth": float(initial_wealth),
        "horizon_years": float(horizon_years),
        "failure_answer": choices["21"],
        "safe_answer": choices["22"],
        "success_answer": choices["23"],
        "q24_scores": q24_scores,
        "fall_answer": choices["31"],
        "stock_count_answer": choices["32"],
        "approach_answer": choices["33"],
        "exclusions": exclusions.strip(),
        "security_loss": security_loss,
        "security_level": security_level,
        "aspiration_return": aspiration_return,
        "aspiration_level": aspiration_level,
        "safe_share": safe_share,
    }
    return profile


def make_csv_row(client_id, profile):
    row = {"client_id": client_id, "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for key in profile:
        if key != "q24_scores":
            row[key] = profile[key]
    for i in range(len(Q24_LABELS)):
        row["q24_" + Q24_LABELS[i]] = profile["q24_scores"][i]
    return row


def show_saved_profile():
    profile = st.session_state["profile"]
    st.subheader("Saved profile")
    fields = [
        "Name",
        "Investment experience (Q2)",
        "Follows markets (Q3)",
        "Preferred horizon for Rs 10 lakh (Q4)",
        "Investable amount (PS1)",
        "Investment horizon used (PS1)",
        "Security level (Q21)",
        "Aspiration level (Q23)",
        "Share wanted completely safe (Q22)",
        "Largest fall they can sit through (Q31)",
        "Number of stocks (Q32)",
        "Overall approach (Q33)",
        "Sectors or companies to avoid (Q34)",
    ]
    exclusions = profile["exclusions"]
    if exclusions == "":
        exclusions = "None given"
    values = [
        profile["name"],
        profile["experience"],
        profile["follows_markets"],
        profile["preferred_horizon"],
        format_rupees(profile["initial_wealth"]),
        str(profile["horizon_years"]) + " years",
        format_rupees(profile["security_level"]) + " (a loss of up to {:.0%})".format(profile["security_loss"]),
        format_rupees(profile["aspiration_level"]) + " ({:.0%} a year over the horizon)".format(profile["aspiration_return"]),
        profile["safe_answer"],
        profile["fall_answer"],
        profile["stock_count_answer"],
        profile["approach_answer"],
        exclusions,
    ]
    st.table(pd.DataFrame({"Field": fields, "Value": values}))

    q24_table = pd.DataFrame(
        {
            "Statement (Q24)": Q24_STATEMENTS,
            "What it shows": Q24_LABELS,
            "Score (1 to 5)": profile["q24_scores"],
        }
    )
    st.table(q24_table)
    st.caption("Client ID: " + st.session_state["client_id"])


def show_intro():
    st.write("Part of the MBA680 investment advisory project. Your answers will be used to build a personal portfolio recommendation for you.")
    st.write("There are no right or wrong answers, and this is not a test of financial knowledge. Answer with what you would actually choose.")
    st.write("All amounts are in rupees. One lakh = Rs 1,00,000. Assume every stated outcome is certain to be paid, with no tax or charges.")


def show_profile_page():
    st.title("Client Profile")
    show_intro()

    with st.form(widget_key("profile_form")):
        name = st.text_input("1. Your name", value=get_saved_value("name", ""))

        st.subheader("About you")
        choices = {}
        choices["2"] = ask_profile_choice("experience", "2. How much investment experience do you have?", EXPERIENCE_OPTIONS)
        choices["3"] = ask_profile_choice("follows_markets", "3. How often do you follow financial markets?", MARKETS_OPTIONS)
        choices["4"] = ask_profile_choice("preferred_horizon", "4. If you had Rs 10,00,000 to invest, how long would you want it invested for?", PREFERRED_HORIZON_OPTIONS)

        st.subheader("Investment set by problem statement 1")
        initial_wealth = st.number_input(
            "Investable amount (Rs)",
            min_value=1000.0,
            value=get_saved_value("initial_wealth", 10000000.0),
            step=100000.0,
            format="%.0f",
        )
        horizon_years = st.number_input(
            "Investment horizon (years)",
            min_value=0.25,
            max_value=40.0,
            value=get_saved_value("horizon_years", 0.25),
            step=0.25,
        )

        st.subheader("What counts as success or failure")
        st.write("Assume you invest Rs 10,00,000 for one year.")
        choices["21"] = ask_profile_choice("failure_answer", "21. What is the lowest year-end value you could accept without calling the investment a failure?", FAILURE_OPTIONS)
        choices["22"] = ask_profile_choice("safe_answer", "22. How much of the Rs 10,00,000 would you want kept completely safe, in deposits or government securities?", SAFE_OPTIONS)
        choices["23"] = ask_profile_choice("success_answer", "23. What year-end value would make you call this a clear success?", SUCCESS_OPTIONS)
        q24_scores = ask_q24()

        st.subheader("What you would want held")
        choices["31"] = ask_profile_choice("fall_answer", "31. How large a fall in portfolio value could you sit through without abandoning the plan?", FALL_OPTIONS)
        choices["32"] = ask_profile_choice("stock_count_answer", "32. How many individual stocks would you be comfortable holding at once?", STOCK_COUNT_OPTIONS)
        choices["33"] = ask_profile_choice("approach_answer", "33. Which best describes your overall approach?", APPROACH_OPTIONS)
        exclusions = st.text_area(
            "34. Any sectors or companies you would refuse to hold, or anything else we should know? (Optional. Leave blank if nothing comes to mind.)",
            value=get_saved_value("exclusions", ""),
        )

        submitted = st.form_submit_button("Save profile")

    if submitted:
        missing = find_missing_answers(name, choices, q24_scores)
        if len(missing) > 0:
            st.error("Please answer question(s): " + ", ".join(missing))
        else:
            profile = build_profile(name, choices, q24_scores, initial_wealth, horizon_years, exclusions)
            client_id = datetime.now().strftime("%Y%m%d-%H%M%S")
            st.session_state["profile"] = profile
            st.session_state["client_id"] = client_id
            add_new_response_row(make_csv_row(client_id, profile))
            st.success("Profile saved. Go to the Risk & Time Quiz page next.")

    if "profile" in st.session_state:
        show_saved_profile()
