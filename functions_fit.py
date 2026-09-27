import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from profile_page import format_rupees, update_response_row
from risk_quiz import CE_TASKS, Q6_OPTIONS


BACKGROUND_WEALTH = 1000000
LAKH = 100000
GAMMA_LOWEST = -20.0
GAMMA_HIGHEST = 100.0
WEIGHTING_LOWEST = 0.20
WEIGHTING_HIGHEST = 2.00
WEIGHTING_STEP = 0.01


def number_text(value):
    return "{:.3f}".format(value)


def certainty_wealth(prize, gamma):
    ratio = 1 + prize / BACKGROUND_WEALTH
    if abs(1 - gamma) < 0.000001:
        mean = math.exp(0.5 * math.log(ratio))
    else:
        power = 1 - gamma
        mean = (0.5 * ratio ** power + 0.5) ** (1 / power)
    return BACKGROUND_WEALTH * mean


def model_ce(prize, gamma):
    return certainty_wealth(prize, gamma) - BACKGROUND_WEALTH


def solve_gamma(prize, ce):
    low = GAMMA_LOWEST
    high = GAMMA_HIGHEST
    if ce >= model_ce(prize, low):
        return low
    if ce <= model_ce(prize, high):
        return high
    for step in range(200):
        middle = (low + high) / 2
        if model_ce(prize, middle) > ce:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def fit_alpha(ce, prize):
    return math.log(0.5) / math.log(ce / prize)


def fit_beta(ce, prize):
    return math.log(0.5) / math.log(abs(ce) / prize)


def fit_lambda(gain, loss, alpha, beta):
    gain_in_lakh = gain / LAKH
    loss_in_lakh = loss / LAKH
    return gain_in_lakh ** alpha / loss_in_lakh ** beta


def probability_weight(p, c):
    top = p ** c
    bottom = (p ** c + (1 - p) ** c) ** (1 / c)
    return top / bottom


def observed_weight(ce, prize, alpha):
    return (ce / prize) ** alpha


def fit_weighting(probabilities, observed_weights):
    best_c = WEIGHTING_LOWEST
    best_error = None
    c = WEIGHTING_LOWEST
    while c <= WEIGHTING_HIGHEST + 0.000001:
        error = 0
        for i in range(len(probabilities)):
            difference = probability_weight(probabilities[i], c) - observed_weights[i]
            error = error + difference * difference
        if best_error is None or error < best_error:
            best_error = error
            best_c = c
        c = c + WEIGHTING_STEP
    return round(best_c, 2)


def fit_time_preference(r_now, r_later):
    delta = 1 / (1 + r_later)
    beta_time = 1 / ((1 + r_now) * delta)
    return delta, beta_time


def fit_all(results):
    fits = {}
    fits["gamma_q9"] = solve_gamma(CE_TASKS["q9"]["prize"], results["q9_ce"])
    fits["gamma_q10"] = solve_gamma(CE_TASKS["q10"]["prize"], results["q10_ce"])
    fits["gamma"] = (fits["gamma_q9"] + fits["gamma_q10"]) / 2

    fits["alpha"] = fit_alpha(results["q11_ce"], CE_TASKS["q11"]["prize"])
    fits["beta"] = fit_beta(results["q12_ce"], CE_TASKS["q12"]["prize"])
    fits["lambda"] = fit_lambda(results["q13_smallest_gain"], results["q13_loss"], fits["alpha"], fits["beta"])
    fits["lambda_simple"] = results["q13_smallest_gain"] / results["q13_loss"]

    fits["weight_q14"] = observed_weight(results["q14_ce"], CE_TASKS["q14"]["prize"], fits["alpha"])
    fits["weight_q15"] = observed_weight(results["q15_ce"], CE_TASKS["q15"]["prize"], fits["alpha"])
    fits["weighting_c"] = fit_weighting([0.05, 0.95], [fits["weight_q14"], fits["weight_q15"]])

    delta, beta_time = fit_time_preference(results["r_now"], results["r_later"])
    fits["time_delta"] = delta
    fits["time_beta"] = beta_time
    fits["present_bias"] = results["r_now"] > results["r_later"]
    return fits


def crra_utility(relative_wealth, gamma):
    if abs(1 - gamma) < 0.000001:
        return np.log(relative_wealth)
    power = 1 - gamma
    return relative_wealth ** power / power


def gamma_meaning(gamma):
    if gamma > 0.05:
        return "Risk averse: concave utility, prefers a sure amount to a fair gamble"
    if gamma < -0.05:
        return "Risk seeking: convex utility, prefers a fair gamble to a sure amount"
    return "About risk neutral: close to a straight line"


def alpha_meaning(alpha):
    if alpha < 1:
        return "Concave for gains: risk averse when gambling over gains"
    if alpha > 1:
        return "Convex for gains: risk seeking when gambling over gains"
    return "Linear for gains"


def beta_meaning(beta):
    if beta < 1:
        return "Convex for losses: risk seeking when facing losses"
    if beta > 1:
        return "Concave for losses: risk averse when facing losses"
    return "Linear for losses"


def lambda_meaning(loss_aversion):
    if loss_aversion > 1:
        return "Loss averse: a loss hurts more than an equal gain pleases"
    if loss_aversion < 1:
        return "Gains weigh more than equal losses (not loss averse)"
    return "Gains and losses weigh the same"


def weighting_meaning(c):
    if c < 1:
        return "Inverse-S: overweights small chances, underweights large chances"
    if c > 1:
        return "S-shaped: underweights small chances, overweights large chances"
    return "Linear: takes probabilities at face value"


def show_design_table():
    st.subheader("How the questionnaire measures these functions")
    st.write("Step 4 uses questions from our questionnaire. Each question pins down one parameter of the utility or value function.")
    table = pd.DataFrame(
        {
            "Question": ["Q9 (+ Q5), Q10", "Q6", "Q11", "Q12", "Q13", "Q14, Q15", "Q18, Q19"],
            "What the person tells us": [
                "Certainty equivalent of a 50-50 coin toss for Rs 10 lakh and Rs 5 lakh",
                "Straight choice between a sure Rs 7 lakh and a 50-50 gamble for Rs 15 lakh",
                "Certainty equivalent of a 50% chance to gain Rs 1 lakh",
                "Certainty equivalent of a 50% chance to lose Rs 1 lakh",
                "Smallest gain that makes a 50-50 toss with a Rs 50,000 loss acceptable",
                "Certainty equivalent of a 5% and a 95% chance of Rs 5 lakh",
                "Extra money needed to wait 6 months, now and in a year",
            ],
            "Parameter": [
                "γ (EUT risk aversion)",
                "Check of γ",
                "α (value curvature for gains)",
                "β (value curvature for losses)",
                "λ (loss aversion)",
                "c (probability weighting)",
                "δ and β (time preference)",
            ],
            "Equation solved": [
                "U(W₀ + CE) = 0.5·U(W₀ + X) + 0.5·U(W₀)",
                "Does the fitted γ predict the same choice?",
                "CE^α = 0.5·X^α",
                "−λ·|CE|^β = 0.5·(−λ·X^β)",
                "0.5·G^α = 0.5·λ·L^β",
                "CE^α = w(p)·X^α",
                "δ = 1/(1 + r_later), β = 1/((1 + r_now)·δ)",
            ],
        }
    )
    st.table(table)


def make_utility_chart(gamma, results):
    gains_in_lakh = np.linspace(0, 10, 200)
    relative_wealth = 1 + gains_in_lakh * LAKH / BACKGROUND_WEALTH
    top_value = crra_utility(1 + 10 * LAKH / BACKGROUND_WEALTH, gamma)
    bottom_value = crra_utility(1.0, gamma)
    utility = (crra_utility(relative_wealth, gamma) - bottom_value) / (top_value - bottom_value)

    ce_in_lakh = model_ce(10 * LAKH, gamma) / LAKH
    answer_in_lakh = results["q9_ce"] / LAKH

    figure, axis = plt.subplots(figsize=(6, 4.5))
    axis.plot(gains_in_lakh, utility, color="tab:blue", linewidth=2, label="Fitted CRRA utility, γ = " + number_text(gamma))
    axis.plot([0, 10], [0, 1], color="gray", linestyle="--", label="Risk neutral (γ = 0)")
    axis.axhline(0.5, color="lightgray", linewidth=1)
    axis.scatter([5], [0.5], color="gray", zorder=3)
    axis.annotate("Expected value Rs 5 lakh", (5, 0.5), textcoords="offset points", xytext=(6, -14), fontsize=8)
    axis.scatter([ce_in_lakh], [0.5], color="tab:red", zorder=3)
    axis.annotate("Model CE", (ce_in_lakh, 0.5), textcoords="offset points", xytext=(6, 6), fontsize=8, color="tab:red")
    axis.scatter([answer_in_lakh], [0.5], color="tab:orange", marker="x", zorder=3)
    axis.annotate("Your Q9 answer", (answer_in_lakh, 0.5), textcoords="offset points", xytext=(6, 18), fontsize=8, color="tab:orange")
    axis.set_xlabel("Gain on top of Rs 10 lakh background wealth (Rs lakh)")
    axis.set_ylabel("Utility (scaled 0 to 1)")
    axis.set_title("EUT utility function (CRRA)")
    axis.legend(fontsize=8, loc="lower right")
    figure.tight_layout()
    return figure


def make_value_chart(alpha, beta, loss_aversion):
    gains = np.linspace(0, 1, 200)
    losses = np.linspace(-1, 0, 200)
    gain_values = gains ** alpha
    loss_values = -loss_aversion * (-losses) ** beta

    figure, axis = plt.subplots(figsize=(6, 4.5))
    axis.plot(gains, gain_values, color="tab:green", linewidth=2, label="Gains: x^α, α = " + number_text(alpha))
    axis.plot(losses, loss_values, color="tab:red", linewidth=2, label="Losses: −λ(−x)^β, β = " + number_text(beta) + ", λ = " + number_text(loss_aversion))
    axis.plot([-1, 1], [-1, 1], color="gray", linestyle="--", label="No loss aversion, linear (v = x)")
    axis.axhline(0, color="black", linewidth=0.8)
    axis.axvline(0, color="black", linewidth=0.8)
    axis.scatter([0], [0], color="black", zorder=3)
    axis.annotate("Kink at the reference point", (0, 0), textcoords="offset points", xytext=(8, -16), fontsize=8)
    axis.set_xlabel("Gain or loss from the reference point (Rs lakh)")
    axis.set_ylabel("Value v(x)")
    axis.set_title("Prospect Theory value function")
    axis.legend(fontsize=8, loc="upper left")
    figure.tight_layout()
    return figure


def make_weighting_chart(c, weight_q14, weight_q15):
    probabilities = np.linspace(0.001, 0.999, 300)
    weights = probability_weight(probabilities, c)

    figure, axis = plt.subplots(figsize=(6, 4.5))
    axis.plot(probabilities, weights, color="tab:purple", linewidth=2, label="Fitted w(p), c = " + "{:.2f}".format(c))
    axis.plot([0, 1], [0, 1], color="gray", linestyle="--", label="Linear w(p) = p")
    axis.scatter([0.05, 0.95], [weight_q14, weight_q15], color="tab:orange", marker="x", zorder=3, label="Your answers (Q14, Q15)")
    axis.set_xlabel("Stated probability p")
    axis.set_ylabel("Decision weight w(p)")
    axis.set_title("Probability weighting function")
    axis.legend(fontsize=8, loc="upper left")
    figure.tight_layout()
    return figure


def make_discount_chart(delta, beta_time):
    months = []
    exponential = []
    quasi_hyperbolic = []
    for month in range(0, 25):
        months.append(month)
        exponential.append(delta ** month)
        if month == 0:
            quasi_hyperbolic.append(1.0)
        else:
            quasi_hyperbolic.append(beta_time * delta ** month)

    figure, axis = plt.subplots(figsize=(6, 4.5))
    axis.plot(months, exponential, color="gray", linestyle="--", label="Exponential: δ^t")
    axis.plot(months, quasi_hyperbolic, color="tab:blue", marker="o", markersize=3, label="Your β–δ discounting: β·δ^t")
    axis.set_xlabel("Months from today")
    axis.set_ylabel("Value today of Rs 1 paid in month t")
    axis.set_title("Time discounting")
    axis.legend(fontsize=8)
    figure.tight_layout()
    return figure


def utility_formula(gamma):
    if abs(1 - gamma) < 0.000001:
        return "U(W) = \\ln W"
    power = number_text(1 - gamma)
    return "U(W) = \\frac{W^{" + power + "}}{" + power + "}"


def check_choice(prize, sure_amount, gamma, options, actual_answer):
    if model_ce(prize, gamma) < sure_amount:
        predicted = options[0]
    else:
        predicted = options[1]
    if predicted == actual_answer:
        match = "Yes"
    else:
        match = "No"
    return predicted, match


def make_check_table(fits, results):
    q6_predicted, q6_match = check_choice(15 * LAKH, 7 * LAKH, fits["gamma"], Q6_OPTIONS, results["q6_answer"])
    table = pd.DataFrame(
        {
            "Question": ["Q6"],
            "Model predicts": [q6_predicted],
            "Actual answer": [results["q6_answer"]],
            "Match": [q6_match],
        }
    )
    return table


def show_utility_section(fits, results):
    st.header("1. Utility function (Expected Utility Theory)")
    st.write("We use constant relative risk aversion (CRRA) utility over total wealth W. The questionnaire frames money as Rs 10 lakh to invest, so we take background wealth W₀ = Rs 10 lakh.")
    st.latex("U(W) = \\frac{W^{1-\\gamma}}{1-\\gamma} \\quad (\\gamma \\neq 1), \\qquad U(W) = \\ln W \\quad (\\gamma = 1)")
    st.latex("U(W_0 + CE) = 0.5\\,U(W_0 + X) + 0.5\\,U(W_0)")
    st.write("For each coin toss we find the γ that makes this equation true at the person's certainty equivalent, using a bisection loop. Their γ is the average of the two. Q5 offers the same toss as Q9 against a sure Rs 5 lakh, so it is used as an extra row of Q9.")

    table = pd.DataFrame(
        {
            "Task": ["Q9 + Q5: 50% of Rs 10,00,000", "Q10: 50% of Rs 5,00,000", "Final γ (average)"],
            "Certainty equivalent": [format_rupees(results["q9_ce"]), format_rupees(results["q10_ce"]), ""],
            "γ": [number_text(fits["gamma_q9"]), number_text(fits["gamma_q10"]), number_text(fits["gamma"])],
        }
    )
    left_column, right_column = st.columns([1, 1])
    with left_column:
        st.table(table)
        st.markdown("**Fitted utility function**")
        st.latex(utility_formula(fits["gamma"]))
        st.write(gamma_meaning(fits["gamma"]) + ".")
        st.write("Risk premium on the Q9 coin toss: " + format_rupees(5 * LAKH - results["q9_ce"]) + " (expected value minus certainty equivalent).")
        if fits["gamma_q9"] == GAMMA_LOWEST or fits["gamma_q9"] == GAMMA_HIGHEST or fits["gamma_q10"] == GAMMA_LOWEST or fits["gamma_q10"] == GAMMA_HIGHEST:
            st.warning("One answer was at the edge of the search range, so γ was capped.")
    with right_column:
        figure = make_utility_chart(fits["gamma"], results)
        st.pyplot(figure)
        plt.close(figure)
        st.caption("The model CE uses the average γ of Q9 and Q10, so it can differ from your Q9 answer.")

    st.markdown("**Check: does the fitted γ predict the person's straight choice in Q6?**")
    st.table(make_check_table(fits, results))
    st.write("Q7 and Q8: " + results["allais_result"] + ". A single utility function under EUT cannot produce the Allais paradox, which is one reason we also fit a Prospect Theory model below.")


def show_value_section(fits, results):
    st.header("2. Value function (Prospect Theory)")
    st.write("Prospect Theory measures gains and losses from a reference point (here, zero change), not total wealth. Amounts are in Rs lakh. At p = 0.5 we take the decision weight as 0.5.")
    st.latex("v(x) = x^{\\alpha} \\quad (x \\ge 0), \\qquad v(x) = -\\lambda(-x)^{\\beta} \\quad (x < 0)")
    st.latex("\\alpha = \\frac{\\ln 0.5}{\\ln(CE_{11}/X)}, \\quad \\beta = \\frac{\\ln 0.5}{\\ln(|CE_{12}|/X)}, \\quad \\lambda = \\frac{G^{\\alpha}}{L^{\\beta}}")

    table = pd.DataFrame(
        {
            "Parameter": ["α (gains)", "β (losses)", "λ (loss aversion)", "Simple ratio G / L"],
            "From": [
                "Q11: CE = " + format_rupees(results["q11_ce"]) + " for X = Rs 1,00,000",
                "Q12: CE = " + format_rupees(results["q12_ce"]) + " for X = Rs 1,00,000",
                "Q13: G = " + format_rupees(results["q13_smallest_gain"]) + ", L = " + format_rupees(results["q13_loss"]),
                "Q13",
            ],
            "Value": [number_text(fits["alpha"]), number_text(fits["beta"]), number_text(fits["lambda"]), number_text(fits["lambda_simple"])],
            "Meaning": [alpha_meaning(fits["alpha"]), beta_meaning(fits["beta"]), lambda_meaning(fits["lambda"]), "λ if the curve were linear"],
        }
    )
    st.table(table)

    left_column, right_column = st.columns([1, 1])
    with left_column:
        st.markdown("**Fitted value function (x in Rs lakh)**")
        st.latex("v(x) = x^{" + number_text(fits["alpha"]) + "} \\quad (x \\ge 0)")
        st.latex("v(x) = -" + number_text(fits["lambda"]) + "\\,(-x)^{" + number_text(fits["beta"]) + "} \\quad (x < 0)")
        st.write("A loss of Rs 1 lakh feels like v(−1) = " + number_text(-fits["lambda"]) + ", while a gain of Rs 1 lakh feels like v(1) = 1.")
        st.caption("Tversky and Kahneman (1992) found α = β = 0.88 and λ = 2.25 for a typical person.")
    with right_column:
        figure = make_value_chart(fits["alpha"], fits["beta"], fits["lambda"])
        st.pyplot(figure)
        plt.close(figure)


def show_weighting_section(fits, results):
    st.header("3. Probability weighting")
    st.write("Using α from above, Q14 and Q15 tell us the decision weight the person puts on a 5% and a 95% chance. We fit the Tversky–Kahneman (1992) weighting function with a grid search.")
    st.latex("w(p) = \\frac{p^{c}}{\\left(p^{c} + (1-p)^{c}\\right)^{1/c}}, \\qquad w(p) = \\left(\\frac{CE}{X}\\right)^{\\alpha}")

    left_column, right_column = st.columns([1, 1])
    with left_column:
        table = pd.DataFrame(
            {
                "Question": ["Q14 (p = 0.05)", "Q15 (p = 0.95)"],
                "Certainty equivalent": [format_rupees(results["q14_ce"]), format_rupees(results["q15_ce"])],
                "Decision weight w(p)": [number_text(fits["weight_q14"]), number_text(fits["weight_q15"])],
            }
        )
        st.table(table)
        st.latex("c = " + "{:.2f}".format(fits["weighting_c"]))
        st.write(weighting_meaning(fits["weighting_c"]) + ".")
        st.caption("Tversky and Kahneman (1992) found c = 0.61 for gains.")
    with right_column:
        figure = make_weighting_chart(fits["weighting_c"], fits["weight_q14"], fits["weight_q15"])
        st.pyplot(figure)
        plt.close(figure)


def show_time_section(fits, results):
    st.header("4. Time preference")
    st.write("From Q18 and Q19 we have monthly discount rates for the near future (r_now) and the far future (r_later). We fit the β–δ (quasi-hyperbolic) model.")
    st.latex("D(0) = 1, \\quad D(t) = \\beta\\,\\delta^{t}, \\quad \\delta = \\frac{1}{1 + r_{later}}, \\quad \\beta = \\frac{1}{(1 + r_{now})\\,\\delta}")

    left_column, right_column = st.columns([1, 1])
    with left_column:
        table = pd.DataFrame(
            {
                "Measure": ["r_now (monthly, Q18)", "r_later (monthly, Q19)", "δ (monthly)", "β (present bias)"],
                "Value": [
                    "{:.2%}".format(results["r_now"]),
                    "{:.2%}".format(results["r_later"]),
                    number_text(fits["time_delta"]),
                    number_text(fits["time_beta"]),
                ],
            }
        )
        st.table(table)
        if fits["present_bias"]:
            st.write("β is below 1, so the person shows **present bias**: money today gets an extra premium over any future date.")
        else:
            st.write("β is 1 or more, so the person does not show present bias.")
    with right_column:
        figure = make_discount_chart(fits["time_delta"], fits["time_beta"])
        st.pyplot(figure)
        plt.close(figure)


def show_summary_table(fits):
    st.header("Summary of fitted parameters")
    table = pd.DataFrame(
        {
            "Parameter": ["γ", "α", "β", "λ", "c", "δ (monthly)", "β (time)"],
            "Model": ["EUT, CRRA", "Prospect Theory", "Prospect Theory", "Prospect Theory", "Probability weighting", "Time preference", "Time preference"],
            "Value": [
                number_text(fits["gamma"]),
                number_text(fits["alpha"]),
                number_text(fits["beta"]),
                number_text(fits["lambda"]),
                "{:.2f}".format(fits["weighting_c"]),
                number_text(fits["time_delta"]),
                number_text(fits["time_beta"]),
            ],
        }
    )
    st.table(table)


def save_fits(fits):
    st.session_state["functions"] = fits
    if "client_id" in st.session_state:
        values = {}
        for key in fits:
            values["fit_" + key] = fits[key]
        update_response_row(st.session_state["client_id"], values)


def show_functions_page():
    st.title("My Utility & Value")
    if "quiz" not in st.session_state:
        st.warning("Please finish the Risk & Time Quiz first. This page is built from those answers.")
        return

    results = st.session_state["quiz"]["results"]
    fits = fit_all(results)
    save_fits(fits)

    show_design_table()
    show_utility_section(fits, results)
    show_value_section(fits, results)
    show_weighting_section(fits, results)
    show_time_section(fits, results)
    show_summary_table(fits)
