import pandas as pd
import streamlit as st

from profile_page import format_rupees, update_response_row, widget_key


FEELING_OPTIONS = ["Very negative", "Negative", "Neutral", "Positive", "Very positive"]
PATIENCE_OPTIONS = ["Under a month", "1-3 months", "3-6 months", "6-12 months", "Over a year"]
FALL_ACTION_OPTIONS = ["Sell everything", "Sell part of it", "Hold", "Buy more"]
SELL_OPTIONS = [
    "The one that is up",
    "The one that is down",
    "Half of each",
    "Whichever has the weaker outlook, regardless of what I paid",
]
LIKERT_OPTIONS = ["1", "2", "3", "4", "5"]

TABLE_COLUMNS = {
    "q9": ["Toss the coin", "Take the guarantee"],
    "q10": ["Toss the coin", "Take the guarantee"],
    "q11": ["Toss the coin", "Take the sure gain"],
    "q12": ["Toss the coin", "Accept the sure loss"],
    "q13": ["Refuse", "Agree to toss"],
    "q14": ["Play the lottery", "Take the guarantee"],
    "q15": ["Play the lottery", "Take the guarantee"],
    "q18": ["Rs 50,000 today", "Wait six months"],
    "q19": ["Rs 50,000 at twelve months", "Wait the extra six months"],
    "q25": LIKERT_OPTIONS,
}

Q5_OPTIONS = ["Rs 5,00,000 for certain", "A 50% chance of Rs 10,00,000, otherwise nothing"]
Q6_OPTIONS = ["Rs 7,00,000 for certain", "A 50% chance of Rs 15,00,000, otherwise nothing"]
Q7_OPTIONS = ["Rs 5,00,000 for certain", "A 10% chance of Rs 25,00,000, an 89% chance of Rs 5,00,000, and a 1% chance of nothing"]
Q8_OPTIONS = ["An 11% chance of Rs 5,00,000, otherwise nothing", "A 10% chance of Rs 25,00,000, otherwise nothing"]

Q9_AMOUNTS = [150000, 250000, 350000, 450000, 600000]
Q9_AMOUNTS_WITH_Q5 = [150000, 250000, 350000, 450000, 500000, 600000]
Q5_ROW_POSITION = 4
Q10_AMOUNTS = [60000, 110000, 160000, 210000, 300000]
Q11_AMOUNTS = [15000, 25000, 35000, 45000, 60000]
Q12_AMOUNTS = [15000, 25000, 35000, 45000, 60000]
Q13_GAINS = [30000, 50000, 75000, 110000, 200000]
Q13_LOSS = 50000
Q13_GAIN_IF_NONE_ACCEPTED = 300000
Q14_AMOUNTS = [10000, 20000, 30000, 45000, 70000]
Q15_AMOUNTS = [300000, 350000, 400000, 435000, 465000]
TIME_TODAY_AMOUNT = 50000
TIME_LATER_AMOUNTS = [52000, 55000, 58000, 63000, 72000]
TIME_PERIOD_MONTHS = 6

CE_TASKS = {
    "q9": {"prize": 1000000, "chance": 0.5, "amounts": Q9_AMOUNTS, "switch_to": 1, "sign": 1},
    "q10": {"prize": 500000, "chance": 0.5, "amounts": Q10_AMOUNTS, "switch_to": 1, "sign": 1},
    "q11": {"prize": 100000, "chance": 0.5, "amounts": Q11_AMOUNTS, "switch_to": 1, "sign": 1},
    "q12": {"prize": 100000, "chance": 0.5, "amounts": Q12_AMOUNTS, "switch_to": 0, "sign": -1},
    "q14": {"prize": 500000, "chance": 0.05, "amounts": Q14_AMOUNTS, "switch_to": 1, "sign": 1},
    "q15": {"prize": 500000, "chance": 0.95, "amounts": Q15_AMOUNTS, "switch_to": 1, "sign": 1},
}

Q25_STATEMENTS = [
    "I risk investment profits more freely than salary.",
    "I lean towards stocks people I know are buying.",
    "My family's choice of bank influences mine.",
    "I wait for more evidence before changing my mind.",
    "I favour analysis that supports my existing view.",
    "Selling at a profit is easier than selling at a loss.",
    "I can pick stocks better than most investors.",
    "A market fall makes me check my portfolio constantly.",
]
Q25_LABELS = [
    "House money effect",
    "Herding",
    "Family influence",
    "Conservatism",
    "Confirmation bias",
    "Disposition effect",
    "Overconfidence",
    "Myopic loss aversion",
]


def make_row_labels(before_text, amounts, after_text):
    labels = []
    for amount in amounts:
        labels.append(before_text + format_rupees(amount) + after_text)
    return labels


def get_saved_answer(key):
    if "quiz" in st.session_state:
        return st.session_state["quiz"]["answers"][key]
    return None


def ask_single(key, question, options):
    saved_index = get_saved_answer(key)
    answer = st.radio(question, options, index=saved_index, key=widget_key("quiz_" + key))
    if answer is None:
        return None
    return options.index(answer)


def ask_table(key, question, note, row_labels, columns):
    st.markdown("**" + question + "**")
    st.caption(note)
    saved_choices = get_saved_answer(key)
    choices = []
    for i in range(len(row_labels)):
        start_index = None
        if saved_choices is not None:
            start_index = saved_choices[i]
        answer = st.radio(row_labels[i], columns, index=start_index, horizontal=True, key=widget_key("quiz_" + key + "_" + str(i)))
        if answer is None:
            choices.append(None)
        else:
            choices.append(columns.index(answer))
    return choices


def ask_risky_choices(answers):
    st.subheader("Choices between risky options")
    st.write("Four straight choices. Pick whichever you would actually take.")
    answers["q5"] = ask_single("q5", "5. Which would you prefer?", Q5_OPTIONS)
    answers["q6"] = ask_single("q6", "6. Which would you prefer?", Q6_OPTIONS)
    answers["q7"] = ask_single("q7", "7. Which would you prefer?", Q7_OPTIONS)
    answers["q8"] = ask_single("q8", "8. And which of these? Answer without going back to change your last answer.", Q8_OPTIONS)


def ask_coin_tosses(answers):
    st.subheader("Coin toss or guaranteed money")
    st.write("Two tables. Each row is a choice between tossing a coin and taking a guaranteed amount. Pick one side in every row.")
    st.write("Most people prefer the toss at the top and switch to the guaranteed amount further down. Please switch only once in each table.")
    answers["q9"] = ask_table(
        "q9",
        "9. A fair coin is tossed. Heads you get Rs 10,00,000, tails you get nothing.",
        "Pick one side in every row.",
        make_row_labels("Guaranteed ", Q9_AMOUNTS, ""),
        TABLE_COLUMNS["q9"],
    )
    answers["q10"] = ask_table(
        "q10",
        "10. A fair coin is tossed. Heads you get Rs 5,00,000, tails you get nothing.",
        "Pick one side in every row.",
        make_row_labels("Guaranteed ", Q10_AMOUNTS, ""),
        TABLE_COLUMNS["q10"],
    )


def ask_gains_and_losses(answers):
    st.subheader("Gains and losses")
    st.write("Same format, but now some outcomes take money away from you rather than adding to it.")
    answers["q11"] = ask_table(
        "q11",
        "11. A coin is tossed. Heads you GAIN Rs 1,00,000, tails nothing happens.",
        "Pick one side in every row.",
        make_row_labels("Gain ", Q11_AMOUNTS, " for sure"),
        TABLE_COLUMNS["q11"],
    )
    answers["q12"] = ask_table(
        "q12",
        "12. A coin is tossed. Heads you LOSE Rs 1,00,000, tails nothing happens.",
        "A sure loss means the money is definitely gone. Pick one side in every row.",
        make_row_labels("Lose ", Q12_AMOUNTS, " for sure"),
        TABLE_COLUMNS["q12"],
    )
    answers["q13"] = ask_table(
        "q13",
        "13. A coin is tossed. Tails you LOSE Rs 50,000. Heads you gain the amount shown.",
        "Would you agree to toss? Pick one side in every row.",
        make_row_labels("Gain ", Q13_GAINS, " on heads"),
        TABLE_COLUMNS["q13"],
    )


def ask_two_lotteries(answers):
    st.subheader("Two lotteries")
    st.write("The same format again. These two look similar but the chances are very different, so please read each one carefully.")
    answers["q14"] = ask_table(
        "q14",
        "14. A lottery pays Rs 5,00,000 with a 5% chance, and nothing otherwise.",
        "A small chance of a large prize. Pick one side in every row.",
        make_row_labels("Guaranteed ", Q14_AMOUNTS, ""),
        TABLE_COLUMNS["q14"],
    )
    answers["q15"] = ask_table(
        "q15",
        "15. A lottery pays Rs 5,00,000 with a 95% chance, and nothing otherwise.",
        "A large chance of the same prize. Pick one side in every row.",
        make_row_labels("Guaranteed ", Q15_AMOUNTS, ""),
        TABLE_COLUMNS["q15"],
    )
    answers["q16"] = ask_single("q16", "16. You bought a stock at Rs 500. A month later it is Rs 450. How do you feel?", FEELING_OPTIONS)
    answers["q17"] = ask_single("q17", "17. Same stock, still Rs 450, but suppose you had bought it at Rs 400. How do you feel?", FEELING_OPTIONS)


def ask_money_now_or_later(answers):
    st.subheader("Money now or money later")
    st.write("Two tables. They look alike, but the timing differs. Please answer each on its own terms rather than trying to match your answers across them.")
    answers["q18"] = ask_table(
        "q18",
        "18. Rs 50,000 today, or more money in six months?",
        "Pick one side in every row.",
        make_row_labels("", TIME_LATER_AMOUNTS, " later"),
        TABLE_COLUMNS["q18"],
    )
    answers["q19"] = ask_table(
        "q19",
        "19. Rs 50,000 in twelve months, or more money in eighteen months?",
        "Nothing is paid today in this table. Pick one side in every row.",
        make_row_labels("", TIME_LATER_AMOUNTS, " at eighteen months"),
        TABLE_COLUMNS["q19"],
    )
    answers["q20"] = ask_single("q20", "20. If an investment of yours underperformed, how long would you give it before changing course?", PATIENCE_OPTIONS)


def ask_behaviour(answers):
    st.subheader("How you tend to behave")
    st.write("Answer for how you actually are, not how you would like to be.")
    answers["q25"] = ask_table(
        "q25",
        "25. How much do you agree with each statement?",
        "1 is strongly disagree, 5 is strongly agree.",
        Q25_STATEMENTS,
        TABLE_COLUMNS["q25"],
    )
    answers["q26"] = ask_single("q26", "26. Your portfolio falls 20% and the whole market has fallen 20% too. What do you do?", FALL_ACTION_OPTIONS)
    answers["q27"] = ask_single("q27", "27. Your portfolio falls 20% but the market is flat. What do you do?", FALL_ACTION_OPTIONS)
    answers["q28"] = ask_single("q28", "28. One stock you own is up 30%, another is down 30%. You need cash and must sell one. Which?", SELL_OPTIONS)


def find_missing_questions(answers):
    missing = []
    for key in answers:
        answer = answers[key]
        if answer is None:
            missing.append(key[1:])
        elif isinstance(answer, list):
            for choice in answer:
                if choice is None:
                    missing.append(key[1:])
                    break
    return missing


def find_switch(choices, switch_to):
    switch_index = None
    for i in range(len(choices)):
        if choices[i] == switch_to:
            switch_index = i
            break
    inconsistent = False
    if switch_index is not None:
        for i in range(switch_index + 1, len(choices)):
            if choices[i] != switch_to:
                inconsistent = True
    return switch_index, inconsistent


def value_at_switch(amounts, switch_index, value_below_first):
    if switch_index is None:
        return amounts[-1]
    if switch_index == 0:
        return (value_below_first + amounts[0]) / 2
    return (amounts[switch_index - 1] + amounts[switch_index]) / 2


def get_switch_row(switch_index):
    if switch_index is None:
        return 0
    return switch_index + 1


def merge_q5_into_q9(q9_choices, q5_answer):
    if q5_answer == 0:
        q5_as_table_choice = 1
    else:
        q5_as_table_choice = 0
    choices = []
    for i in range(len(q9_choices)):
        if i == Q5_ROW_POSITION:
            choices.append(q5_as_table_choice)
        choices.append(q9_choices[i])
    return choices


def score_ce_task(key, choices, amounts):
    task = CE_TASKS[key]
    switch_index, inconsistent = find_switch(choices, task["switch_to"])
    ce = value_at_switch(amounts, switch_index, 0) * task["sign"]
    expected_value = task["chance"] * task["prize"] * task["sign"]
    result = {}
    result[key + "_switch_row"] = get_switch_row(switch_index)
    if switch_index is None:
        result[key + "_switch_amount"] = 0
    else:
        result[key + "_switch_amount"] = amounts[switch_index]
    result[key + "_ce"] = ce
    result[key + "_expected_value"] = expected_value
    result[key + "_inconsistent"] = inconsistent
    return result


def score_mixed_gamble(choices):
    switch_index, inconsistent = find_switch(choices, 1)
    if switch_index is None:
        smallest_gain = Q13_GAIN_IF_NONE_ACCEPTED
    else:
        smallest_gain = Q13_GAINS[switch_index]
    result = {}
    result["q13_switch_row"] = get_switch_row(switch_index)
    result["q13_smallest_gain"] = smallest_gain
    result["q13_loss"] = Q13_LOSS
    result["q13_inconsistent"] = inconsistent
    return result


def score_time_task(key, choices, prefix):
    switch_index, inconsistent = find_switch(choices, 1)
    later_amount = value_at_switch(TIME_LATER_AMOUNTS, switch_index, TIME_TODAY_AMOUNT)
    six_month_rate = later_amount / TIME_TODAY_AMOUNT - 1
    monthly_rate = (1 + six_month_rate) ** (1 / TIME_PERIOD_MONTHS) - 1
    result = {}
    result[key + "_switch_row"] = get_switch_row(switch_index)
    result[key + "_inconsistent"] = inconsistent
    result[prefix + "_six_month"] = six_month_rate
    result[prefix] = monthly_rate
    return result


def score_allais(q7_answer, q8_answer):
    if q7_answer == 0 and q8_answer == 0:
        return "Consistent with EUT (safer option both times)"
    if q7_answer == 1 and q8_answer == 1:
        return "Consistent with EUT (riskier option both times)"
    if q7_answer == 0 and q8_answer == 1:
        return "Allais paradox (certainty effect)"
    return "Reverse Allais pattern (not consistent with EUT)"


def score_quiz(answers):
    results = {}
    results["q5_answer"] = Q5_OPTIONS[answers["q5"]]
    results["q6_answer"] = Q6_OPTIONS[answers["q6"]]
    results["q7_answer"] = Q7_OPTIONS[answers["q7"]]
    results["q8_answer"] = Q8_OPTIONS[answers["q8"]]
    results["allais_result"] = score_allais(answers["q7"], answers["q8"])
    for key in CE_TASKS:
        if key == "q9":
            q9_choices = merge_q5_into_q9(answers["q9"], answers["q5"])
            results.update(score_ce_task("q9", q9_choices, Q9_AMOUNTS_WITH_Q5))
        else:
            results.update(score_ce_task(key, answers[key], CE_TASKS[key]["amounts"]))
    results.update(score_mixed_gamble(answers["q13"]))
    results["q16_feeling"] = answers["q16"] + 1
    results["q17_feeling"] = answers["q17"] + 1
    results["reference_gap"] = results["q17_feeling"] - results["q16_feeling"]
    results.update(score_time_task("q18", answers["q18"], "r_now"))
    results.update(score_time_task("q19", answers["q19"], "r_later"))
    results["present_bias"] = results["r_now"] > results["r_later"]
    results["q20_answer"] = PATIENCE_OPTIONS[answers["q20"]]
    for i in range(len(Q25_LABELS)):
        results["q25_" + Q25_LABELS[i]] = answers["q25"][i] + 1
    results["q26_answer"] = FALL_ACTION_OPTIONS[answers["q26"]]
    results["q27_answer"] = FALL_ACTION_OPTIONS[answers["q27"]]
    results["q28_answer"] = SELL_OPTIONS[answers["q28"]]
    return results


def yearly_rate(monthly_rate):
    return (1 + monthly_rate) ** 12 - 1


def switch_text(switch_row):
    if switch_row == 0:
        return "Never switched"
    return "Row " + str(switch_row)


def switch_amount_text(switch_amount):
    if switch_amount == 0:
        return "Never switched"
    return "At " + format_rupees(switch_amount)


def consistency_text(inconsistent):
    if inconsistent:
        return "Switched back (first switch used)"
    return "Consistent"


def q5_meaning(answer_text):
    if answer_text == Q5_OPTIONS[0]:
        return "Risk averse: turned down a fair bet"
    return "Not risk averse at this stake"


def q6_meaning(answer_text):
    if answer_text == Q6_OPTIONS[0]:
        return "Strongly risk averse: gave up Rs 50,000 of expected value for certainty"
    return "Takes the bet when it pays a small premium"


def make_risky_choice_table(results):
    table = pd.DataFrame(
        {
            "Question": ["Q5", "Q6", "Q7 and Q8"],
            "Answer": [
                results["q5_answer"],
                results["q6_answer"],
                "Q7: " + results["q7_answer"] + " | Q8: " + results["q8_answer"],
            ],
            "What it shows": [
                q5_meaning(results["q5_answer"]),
                q6_meaning(results["q6_answer"]),
                results["allais_result"],
            ],
        }
    )
    return table


def make_ce_table(results):
    names = {
        "q9": "Q9 + Q5. 50% of Rs 10,00,000",
        "q10": "Q10. 50% of Rs 5,00,000",
        "q11": "Q11. 50% gain of Rs 1,00,000",
        "q12": "Q12. 50% loss of Rs 1,00,000",
        "q14": "Q14. 5% of Rs 5,00,000",
        "q15": "Q15. 95% of Rs 5,00,000",
    }
    tasks = []
    switch_points = []
    ces = []
    expected_values = []
    ratios = []
    consistency = []
    for key in CE_TASKS:
        tasks.append(names[key])
        switch_points.append(switch_amount_text(results[key + "_switch_amount"]))
        ces.append(format_rupees(results[key + "_ce"]))
        expected_values.append(format_rupees(results[key + "_expected_value"]))
        ratios.append(round(results[key + "_ce"] / results[key + "_expected_value"], 2))
        consistency.append(consistency_text(results[key + "_inconsistent"]))
    table = pd.DataFrame(
        {
            "Task": tasks,
            "Switch point": switch_points,
            "Certainty equivalent": ces,
            "Expected value": expected_values,
            "CE / EV": ratios,
            "Consistency": consistency,
        }
    )
    return table


def make_time_table(results):
    table = pd.DataFrame(
        {
            "Task": ["Q18. Today vs 6 months", "Q19. 12 vs 18 months"],
            "Switch point": [switch_text(results["q18_switch_row"]), switch_text(results["q19_switch_row"])],
            "6-month rate": ["{:.2%}".format(results["r_now_six_month"]), "{:.2%}".format(results["r_later_six_month"])],
            "Monthly rate": ["{:.2%}".format(results["r_now"]), "{:.2%}".format(results["r_later"])],
            "Yearly rate": ["{:.2%}".format(yearly_rate(results["r_now"])), "{:.2%}".format(yearly_rate(results["r_later"]))],
            "Consistency": [consistency_text(results["q18_inconsistent"]), consistency_text(results["q19_inconsistent"])],
        }
    )
    return table


def strength_text(score):
    if score >= 4:
        return "Strong"
    if score <= 2:
        return "Weak"
    return "Moderate"


def make_behaviour_table(results):
    scores = []
    strengths = []
    for label in Q25_LABELS:
        score = results["q25_" + label]
        scores.append(score)
        strengths.append(strength_text(score))
    table = pd.DataFrame(
        {
            "Statement (Q25)": Q25_STATEMENTS,
            "What it shows": Q25_LABELS,
            "Score (1 to 5)": scores,
            "Signal": strengths,
        }
    )
    return table


def show_inconsistency_warnings(results):
    table_keys = ["q9", "q10", "q11", "q12", "q13", "q14", "q15", "q18", "q19"]
    inconsistent_questions = []
    for key in table_keys:
        if results[key + "_inconsistent"]:
            inconsistent_questions.append(key[1:])
    if len(inconsistent_questions) > 0:
        st.warning("Your answers were inconsistent in question(s) " + ", ".join(inconsistent_questions) + ": you switched more than once. We used your first switch.")


def show_edge_warnings(results):
    never_switched = []
    for key in ["q9", "q10", "q11", "q12", "q14", "q15"]:
        if results[key + "_switch_row"] == 0:
            never_switched.append(key[1:])
    if len(never_switched) > 0:
        st.warning("You never switched in question(s) " + ", ".join(never_switched) + ", so the certainty equivalent is at least the last amount shown. We used that amount.")
    switched_in_first_row = []
    for key in ["q9", "q10", "q11", "q12", "q14", "q15"]:
        if results[key + "_switch_row"] == 1:
            switched_in_first_row.append(key[1:])
    if len(switched_in_first_row) > 0:
        st.warning("You switched in the first row of question(s) " + ", ".join(switched_in_first_row) + ", so the certainty equivalent is below the first amount shown. We used half of the first amount.")
    if results["q13_switch_row"] == 0:
        st.warning("In question 13 you refused every toss, so we used a gain of " + format_rupees(Q13_GAIN_IF_NONE_ACCEPTED) + ".")
    if results["q18_switch_row"] == 0 or results["q19_switch_row"] == 0:
        st.warning("In question 18 or 19 you never chose to wait, so that discount rate is at least the highest rate shown.")


def show_summary(results):
    st.header("Your results")
    show_inconsistency_warnings(results)
    show_edge_warnings(results)

    st.subheader("Choices between risky options")
    st.table(make_risky_choice_table(results))

    st.subheader("Certainty equivalents")
    st.table(make_ce_table(results))
    st.caption("CE / EV below 1 means you prefer safety (risk averse). Above 1 means you prefer the gamble (risk seeking). For the loss in Q12, a ratio below 1 means you prefer to gamble on the loss. Q5 offers the same coin toss as Q9 against a sure Rs 5,00,000, so it is used as an extra row of Q9.")

    st.subheader("Mixed gamble (loss aversion)")
    st.write(
        "Smallest gain you accepted against a loss of "
        + format_rupees(results["q13_loss"])
        + ": **"
        + format_rupees(results["q13_smallest_gain"])
        + "** ("
        + switch_text(results["q13_switch_row"])
        + ", "
        + consistency_text(results["q13_inconsistent"]).lower()
        + ")."
    )

    st.subheader("Reference point")
    st.write("Q16 (bought at Rs 500, now Rs 450): " + FEELING_OPTIONS[results["q16_feeling"] - 1])
    st.write("Q17 (bought at Rs 400, now Rs 450): " + FEELING_OPTIONS[results["q17_feeling"] - 1])
    if results["reference_gap"] > 0:
        st.info("The price is the same in both cases, but you feel better when you bought lower. You judge outcomes against the purchase price (reference dependence).")
    else:
        st.info("You feel the same or worse despite the lower purchase price, so the purchase price does not drive your feelings much.")

    st.subheader("Time preference")
    st.table(make_time_table(results))
    if results["present_bias"]:
        st.info("You are more impatient about the near future than the far future. This is called present bias.")
    st.write("Q20. Time given to an underperforming investment: " + results["q20_answer"])

    st.subheader("How you tend to behave")
    st.table(make_behaviour_table(results))
    st.write("Q26. Portfolio and market both fall 20%: " + results["q26_answer"])
    st.write("Q27. Portfolio falls 20%, market flat: " + results["q27_answer"])
    st.write("Q28. Must sell one of a winner (+30%) or a loser (-30%): " + results["q28_answer"])
    if results["q28_answer"] == SELL_OPTIONS[0]:
        st.info("Selling the winner and keeping the loser is a sign of the disposition effect.")


def answers_to_text(answer):
    if isinstance(answer, list):
        text = ""
        for choice in answer:
            text = text + str(choice + 1)
        return text
    return str(answer + 1)


def save_quiz(answers, results):
    st.session_state["quiz"] = {"answers": answers, "results": results}
    if "client_id" in st.session_state:
        values = {}
        for key in results:
            values[key] = results[key]
        for key in answers:
            values["raw_" + key] = answers_to_text(answers[key])
        update_response_row(st.session_state["client_id"], values)


def show_risk_quiz_page():
    st.title("Risk & Time Quiz")
    if "profile" not in st.session_state:
        st.warning("Please fill the Client Profile first, so your answers can be saved.")

    answers = {}
    with st.form(widget_key("risk_quiz_form")):
        ask_risky_choices(answers)
        ask_coin_tosses(answers)
        ask_gains_and_losses(answers)
        ask_two_lotteries(answers)
        ask_money_now_or_later(answers)
        ask_behaviour(answers)
        submitted = st.form_submit_button("Submit quiz")

    if submitted:
        missing = find_missing_questions(answers)
        if len(missing) > 0:
            st.error("Please answer every row of question(s): " + ", ".join(missing))
        else:
            results = score_quiz(answers)
            save_quiz(answers, results)
            st.success("Quiz saved. Go to the Personality page next.")

    if "quiz" in st.session_state:
        show_summary(st.session_state["quiz"]["results"])
