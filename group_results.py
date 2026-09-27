import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from profile_page import format_rupees
from personality import TRAITS, level_text
from functions_fit import crra_utility, number_text, BACKGROUND_WEALTH, LAKH
from investors import get_investor_ids, build_investor
from portfolio import build_portfolios, range_text
from advice import build_advice


LINE_COLORS = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]


def yes_no(value):
    if value:
        return "Yes"
    return "No"


def percent_text(value):
    return "{:.2%}".format(value)


def make_table(labels, investors, value_function):
    table = {"Measure": labels}
    for investor_id in investors:
        values = value_function(investors[investor_id])
        table[investor_id] = values
    return pd.DataFrame(table)


def profile_values(investor):
    profile = investor["profile"]
    return [
        profile["experience"],
        profile["follows_markets"],
        profile["preferred_horizon"],
        "{:.0%}".format(profile["security_loss"]),
        profile["safe_answer"],
        "{:.0%}".format(profile["aspiration_return"]),
        profile["fall_answer"],
        profile["stock_count_answer"],
        profile["approach_answer"],
    ]


PROFILE_LABELS = [
    "Q2. Investment experience",
    "Q3. Follows markets",
    "Q4. Preferred horizon",
    "Q21. Largest yearly loss accepted",
    "Q22. Share kept completely safe",
    "Q23. Yearly return that is a clear success",
    "Q31. Fall they can sit through",
    "Q32. Number of stocks",
    "Q33. Overall approach",
]


def quiz_values(investor):
    results = investor["results"]
    return [
        results["q5_answer"],
        results["q6_answer"],
        results["allais_result"],
        format_rupees(results["q9_ce"]),
        format_rupees(results["q10_ce"]),
        format_rupees(results["q11_ce"]),
        format_rupees(results["q12_ce"]),
        format_rupees(results["q13_smallest_gain"]),
        format_rupees(results["q14_ce"]),
        format_rupees(results["q15_ce"]),
        str(results["reference_gap"]),
        percent_text(results["r_now"]),
        percent_text(results["r_later"]),
        yes_no(results["present_bias"]),
        results["q20_answer"],
        results["q26_answer"],
        results["q27_answer"],
        results["q28_answer"],
    ]


QUIZ_LABELS = [
    "Q5. Rs 5 lakh sure vs 50% of Rs 10 lakh",
    "Q6. Rs 7 lakh sure vs 50% of Rs 15 lakh",
    "Q7 and Q8. Allais pair",
    "Q9 + Q5. CE of 50% of Rs 10 lakh",
    "Q10. CE of 50% of Rs 5 lakh",
    "Q11. CE of 50% gain of Rs 1 lakh",
    "Q12. CE of 50% loss of Rs 1 lakh",
    "Q13. Smallest gain accepted vs Rs 50,000 loss",
    "Q14. CE of 5% of Rs 5 lakh (EV Rs 25,000)",
    "Q15. CE of 95% of Rs 5 lakh (EV Rs 4,75,000)",
    "Q16/Q17. Reference point gap (feeling points)",
    "Q18. Monthly discount rate, now",
    "Q19. Monthly discount rate, later",
    "Present bias",
    "Q20. Patience with underperformance",
    "Q26. Portfolio and market fall 20%",
    "Q27. Portfolio falls 20%, market flat",
    "Q28. Must sell winner or loser",
]


def trait_values(investor):
    values = []
    for trait in TRAITS:
        score = investor["traits"][trait]
        values.append("{:.2f}".format(score) + " (" + level_text(score) + ")")
    return values


def fit_values(investor):
    fits = investor["fits"]
    return [
        number_text(fits["gamma"]),
        number_text(fits["alpha"]),
        number_text(fits["beta"]),
        number_text(fits["lambda"]),
        number_text(fits["lambda_simple"]),
        "{:.2f}".format(fits["weighting_c"]),
        number_text(fits["time_delta"]),
        number_text(fits["time_beta"]),
    ]


FIT_LABELS = [
    "γ (CRRA risk aversion)",
    "α (value curve, gains)",
    "β (value curve, losses)",
    "λ (loss aversion)",
    "Simple G / L",
    "c (probability weighting)",
    "δ (monthly)",
    "β (time, present bias)",
]


def bias_values(investor):
    results = investor["results"]
    profile = investor["profile"]
    values = []
    for score in profile["q24_scores"]:
        values.append(score)
    for label in ["House money effect", "Herding", "Family influence", "Conservatism", "Confirmation bias", "Disposition effect", "Overconfidence", "Myopic loss aversion"]:
        values.append(results["q25_" + label])
    return values


BIAS_LABELS = [
    "Q24. Loss focus",
    "Q24. Gain focus",
    "Q24. Certainty preference",
    "Q24. Mental accounting",
    "Q24. Layered (BPT) thinking",
    "Q25. House money effect",
    "Q25. Herding",
    "Q25. Family influence",
    "Q25. Conservatism",
    "Q25. Confirmation bias",
    "Q25. Disposition effect",
    "Q25. Overconfidence",
    "Q25. Myopic loss aversion",
]


def add_portfolios(investors):
    for investor_id in investors:
        investor = investors[investor_id]
        investor["portfolios"] = build_portfolios(investor["profile"], investor["results"], investor["answers"], investor["traits"], investor["fits"])
        investor["advice"] = build_advice(investor["profile"], investor["results"], investor["answers"], investor["traits"], investor["fits"])


def portfolio_values(investor):
    portfolios = investor["portfolios"]
    eut = portfolios["eut"]
    bpt = portfolios["bpt"]
    if eut["raw_share"] is None:
        raw_text = "No finite optimum"
    else:
        raw_text = "{:.2f}".format(eut["raw_share"])
    if portfolios["quality"]["reliable"]:
        reliable_text = "Yes"
    else:
        reliable_text = "No (" + str(portfolios["quality"]["warning_signs"]) + " warning signs)"
    return [
        reliable_text,
        "{:.3f}".format(portfolios["fear_hope"]["q"]) + " (" + portfolios["fear_hope"]["label"] + ")",
        raw_text,
        range_text(eut["equity_low"], eut["equity_high"]),
        range_text(bpt["security_low"], bpt["security_high"]),
        range_text(bpt["aspiration_low"], bpt["aspiration_high"]),
    ]


PORTFOLIO_LABELS = [
    "Risk ladders reliable?",
    "SP/A fear share q",
    "EUT raw w* = 0.07 / (γ × 0.04)",
    "EUT equity share",
    "SP/A–BPT security layer",
    "SP/A–BPT aspiration layer",
]


def advice_values(investor):
    themes = []
    for item in investor["advice"]:
        themes.append(item["theme"])
    return ["; ".join(themes)]


def make_portfolio_overlay(investors):
    labels = []
    safe_shares = []
    risky_shares = []
    for investor_id in investors:
        portfolios = investors[investor_id]["portfolios"]
        labels.append(investor_id + "\nEUT")
        safe_shares.append(portfolios["eut"]["safe"] * 100)
        risky_shares.append(portfolios["eut"]["equity"] * 100)
        labels.append(investor_id + "\nSP/A–BPT")
        safe_shares.append(portfolios["bpt"]["security"] * 100)
        risky_shares.append(portfolios["bpt"]["aspiration"] * 100)

    figure, axis = plt.subplots(figsize=(8, 4.5))
    axis.bar(labels, safe_shares, color="tab:blue", label="Safe: debt / security layer")
    axis.bar(labels, risky_shares, bottom=safe_shares, color="tab:orange", label="Risky: equity / aspiration layer")
    for i in range(len(labels)):
        axis.text(i, safe_shares[i] + risky_shares[i] / 2, "{:.0f}%".format(risky_shares[i]), ha="center", va="center", fontsize=9)
    axis.set_ylim(0, 100)
    axis.set_ylabel("Share of the portfolio (%)")
    axis.set_title("EUT and SP/A–BPT portfolios (middle of each range)")
    axis.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
    figure.tight_layout()
    return figure


def make_utility_overlay(investors):
    gains_in_lakh = np.linspace(0, 10, 200)
    relative_wealth = 1 + gains_in_lakh * LAKH / BACKGROUND_WEALTH
    figure, axis = plt.subplots(figsize=(6, 4.5))
    color_number = 0
    for investor_id in investors:
        gamma = investors[investor_id]["fits"]["gamma"]
        top_value = crra_utility(1 + 10 * LAKH / BACKGROUND_WEALTH, gamma)
        bottom_value = crra_utility(1.0, gamma)
        utility = (crra_utility(relative_wealth, gamma) - bottom_value) / (top_value - bottom_value)
        axis.plot(gains_in_lakh, utility, color=LINE_COLORS[color_number], linewidth=2, label=investor_id + ", γ = " + number_text(gamma))
        color_number = color_number + 1
    axis.plot([0, 10], [0, 1], color="gray", linestyle="--", label="Risk neutral")
    axis.set_xlabel("Gain on top of Rs 10 lakh background wealth (Rs lakh)")
    axis.set_ylabel("Utility (scaled 0 to 1)")
    axis.set_title("EUT utility functions")
    axis.legend(fontsize=8, loc="lower right")
    figure.tight_layout()
    return figure


def make_value_overlay(investors):
    gains = np.linspace(0, 1, 200)
    losses = np.linspace(-1, 0, 200)
    figure, axis = plt.subplots(figsize=(6, 4.5))
    color_number = 0
    for investor_id in investors:
        fits = investors[investor_id]["fits"]
        color = LINE_COLORS[color_number]
        label = investor_id + ": α = " + "{:.2f}".format(fits["alpha"]) + ", β = " + "{:.2f}".format(fits["beta"]) + ", λ = " + "{:.2f}".format(fits["lambda"])
        axis.plot(gains, gains ** fits["alpha"], color=color, linewidth=2, label=label)
        axis.plot(losses, -fits["lambda"] * (-losses) ** fits["beta"], color=color, linewidth=2)
        color_number = color_number + 1
    axis.plot([-1, 1], [-1, 1], color="gray", linestyle="--", label="Linear, no loss aversion")
    axis.axhline(0, color="black", linewidth=0.8)
    axis.axvline(0, color="black", linewidth=0.8)
    axis.set_xlabel("Gain or loss from the reference point (Rs lakh)")
    axis.set_ylabel("Value v(x)")
    axis.set_title("Prospect Theory value functions")
    axis.legend(fontsize=7, loc="upper left")
    figure.tight_layout()
    return figure


def make_radar_overlay(investors):
    angles = []
    for i in range(len(TRAITS)):
        angles.append(2 * np.pi * i / len(TRAITS))
    angles.append(angles[0])

    figure = plt.figure(figsize=(5.5, 5.5))
    axis = figure.add_subplot(111, polar=True)
    color_number = 0
    for investor_id in investors:
        values = []
        for trait in TRAITS:
            values.append(investors[investor_id]["traits"][trait])
        values.append(values[0])
        color = LINE_COLORS[color_number]
        axis.plot(angles, values, color=color, linewidth=2, label=investor_id)
        axis.fill(angles, values, color=color, alpha=0.1)
        color_number = color_number + 1
    axis.set_xticks(angles[:-1])
    axis.set_xticklabels(TRAITS, fontsize=9)
    axis.set_ylim(0, 5)
    axis.set_yticks([1, 2, 3, 4, 5])
    axis.set_title("Big Five profiles", pad=20)
    axis.legend(fontsize=8, loc="upper right", bbox_to_anchor=(1.25, 1.1))
    figure.tight_layout()
    return figure


def show_chart(figure):
    st.pyplot(figure)
    plt.close(figure)


def show_group_results_page():
    st.title("Group Results")
    investor_ids = get_investor_ids()
    if len(investor_ids) == 0:
        st.warning("No survey responses found. Run import_responses.py first.")
        return
    st.write("Survey outcomes for the " + str(len(investor_ids)) + " investors in our peer group. Investors are shown by ID only; names are not stored in the portal.")
    st.write("To see one investor's full results, pick them in the sidebar and open any page.")

    investors = {}
    for investor_id in investor_ids:
        investors[investor_id] = build_investor(investor_id)
    add_portfolios(investors)

    st.header("Profile and goals")
    st.table(make_table(PROFILE_LABELS, investors, profile_values))

    st.header("Risk and time answers")
    st.table(make_table(QUIZ_LABELS, investors, quiz_values))

    st.header("Behavioural statements (1 to 5)")
    st.table(make_table(BIAS_LABELS, investors, bias_values))

    st.header("Personality (BFI-2-XS)")
    left_column, right_column = st.columns([1, 1])
    with left_column:
        st.table(make_table(TRAITS, investors, trait_values))
    with right_column:
        show_chart(make_radar_overlay(investors))

    st.header("Utility and value functions")
    st.table(make_table(FIT_LABELS, investors, fit_values))
    left_column, right_column = st.columns([1, 1])
    with left_column:
        show_chart(make_utility_overlay(investors))
    with right_column:
        show_chart(make_value_overlay(investors))

    st.header("Portfolios (Step 5)")
    st.table(make_table(PORTFOLIO_LABELS, investors, portfolio_values))
    show_chart(make_portfolio_overlay(investors))
    st.caption("The SP/A–BPT portfolio is the recommendation for every investor; EUT is a benchmark.")

    st.header("Personality-based advice themes (Step 6)")
    st.table(make_table(["Advice themes"], investors, advice_values))
