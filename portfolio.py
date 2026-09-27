import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from profile_page import format_rupees, update_response_row
from risk_quiz import Q5_OPTIONS, Q9_AMOUNTS, find_switch, value_at_switch


EQUITY_PREMIUM = 0.07
EQUITY_VOLATILITY = 0.20
CAPPED_EQUITY_LOW = 0.90
CAPPED_EQUITY_HIGH = 1.00
LAYER_RANGE_WIDTH = 0.05
UNRELIABLE_EXTRA_SECURITY = 0.20
MAX_SECURITY_START = 0.95
WARNING_SIGNS_LIMIT = 4
STRESS_FALL = 0.20
OPEN_MINDED_LIMIT = 3.0
OVERCONFIDENCE_LIMIT = 5

LADDERS = ["q9", "q10", "q11", "q12", "q13", "q14", "q15", "q18", "q19"]

FALL_LIMITS = {
    "Under 10%": 0.10,
    "10-20%": 0.20,
    "20-30%": 0.30,
    "More than 30%": 1.00,
}


def is_straight_lined(results, key):
    switch_row = results[key + "_switch_row"]
    if switch_row == 0:
        return True
    if switch_row == 1 and not results[key + "_inconsistent"]:
        return True
    return False


def find_straight_lined(results):
    straight_lined = []
    for key in LADDERS:
        if is_straight_lined(results, key):
            straight_lined.append(key.upper())
    return straight_lined


def accepted_negative_gamble(results):
    if results["q13_switch_row"] == 0:
        return False
    return results["q13_smallest_gain"] < results["q13_loss"]


def ladder_only_q9_ce(answers):
    switch_index, inconsistent = find_switch(answers["q9"], 1)
    return value_at_switch(Q9_AMOUNTS, switch_index, 0)


def has_framing_effect(results, answers):
    ladder_ce = ladder_only_q9_ce(answers)
    took_certain_in_q5 = results["q5_answer"] == Q5_OPTIONS[0]
    return ladder_ce > 500000 and took_certain_in_q5


def assess_data_quality(results, answers):
    straight_lined = find_straight_lined(results)
    negative_gamble = accepted_negative_gamble(results)
    warning_signs = len(straight_lined)
    if negative_gamble:
        warning_signs = warning_signs + 1
    quality = {
        "straight_lined": straight_lined,
        "negative_gamble": negative_gamble,
        "warning_signs": warning_signs,
        "reliable": warning_signs < WARNING_SIGNS_LIMIT,
        "allais": results["allais_result"].startswith("Allais paradox"),
        "framing": has_framing_effect(results, answers),
        "ladder_q9_ce": ladder_only_q9_ce(answers),
    }
    return quality


def eut_portfolio(gamma):
    variance = EQUITY_VOLATILITY ** 2
    if gamma <= 0:
        raw_share = None
    else:
        raw_share = EQUITY_PREMIUM / (gamma * variance)
    if raw_share is None or raw_share > 1:
        equity_low = CAPPED_EQUITY_LOW
        equity_high = CAPPED_EQUITY_HIGH
        capped = True
    else:
        equity_low = raw_share
        equity_high = raw_share
        capped = False
    equity = (equity_low + equity_high) / 2
    eut = {
        "raw_share": raw_share,
        "equity_low": equity_low,
        "equity_high": equity_high,
        "equity": equity,
        "safe": 1 - equity,
        "capped": capped,
    }
    return eut


def bpt_portfolio(profile, quality):
    base_security = profile["safe_share"]
    extra_security = 0.0
    if not quality["reliable"]:
        extra_security = UNRELIABLE_EXTRA_SECURITY
    security_low = min(base_security + extra_security, MAX_SECURITY_START)
    security_high = min(security_low + LAYER_RANGE_WIDTH, 1.0)
    security = (security_low + security_high) / 2
    bpt = {
        "base_security": base_security,
        "extra_security": extra_security,
        "security_low": security_low,
        "security_high": security_high,
        "security": security,
        "aspiration_low": 1 - security_high,
        "aspiration_high": 1 - security_low,
        "aspiration": 1 - security,
    }
    return bpt


def fear_and_hope(profile):
    fear = profile["q24_scores"][0]
    hope = profile["q24_scores"][1]
    q = fear / (fear + hope)
    if q > 0.5:
        label = "Fear-dominant"
    elif q < 0.5:
        label = "Hope-dominant"
    else:
        label = "Balanced between fear and hope"
    return {"fear": fear, "hope": hope, "q": q, "label": label}


def underweights_both_chances(results):
    small_chance_low = results["q14_ce"] < results["q14_expected_value"]
    large_chance_low = results["q15_ce"] < results["q15_expected_value"]
    return small_chance_low and large_chance_low


def aspiration_composition(traits, results, quality):
    lines = []
    if traits["Open-Mindedness"] < OPEN_MINDED_LIMIT:
        lines.append("Familiar large-cap or broad-index equity only. No thematic or alternative funds (Open-Mindedness below 3).")
    else:
        lines.append("Broad equity index as the core, plus a modest international or thematic satellite (Open-Mindedness 3 or more).")
    if quality["reliable"] and underweights_both_chances(results):
        lines.append("No concentrated single-stock or lottery-like bets (certainty equivalents below expected value at both 5% and 95%).")
    if results["q25_Overconfidence"] >= OVERCONFIDENCE_LIMIT:
        lines.append("A small number of individual holdings, rebalanced by fixed rules (overconfidence 5 out of 5).")
    return lines


def security_composition():
    return "Liquid and debt funds, fixed deposits or government securities."


def stress_loss(equity_share):
    return equity_share * STRESS_FALL


def build_portfolios(profile, results, answers, traits, fits):
    quality = assess_data_quality(results, answers)
    portfolios = {
        "quality": quality,
        "eut": eut_portfolio(fits["gamma"]),
        "bpt": bpt_portfolio(profile, quality),
        "fear_hope": fear_and_hope(profile),
        "aspiration_lines": aspiration_composition(traits, results, quality),
        "fall_limit": FALL_LIMITS[profile["fall_answer"]],
    }
    return portfolios


def percent_text(value):
    return "{:.1%}".format(value)


def range_text(low, high):
    if abs(high - low) < 0.0001:
        return "{:.0%}".format(low)
    return "{:.0%}".format(low) + " to " + "{:.0%}".format(high)


def yes_no(value):
    if value:
        return "Yes"
    return "No"


def make_quality_table(quality):
    straight_text = "None"
    if len(quality["straight_lined"]) > 0:
        straight_text = ", ".join(quality["straight_lined"])
    if quality["reliable"]:
        verdict = "Usable: fitted parameters can be used"
    else:
        verdict = "Unreliable: build the portfolio from stated preferences"
    table = pd.DataFrame(
        {
            "Check": [
                "Straight-lined ladders (same answer in every row)",
                "Accepted a negative expected value gamble in Q13",
                "Warning signs (limit " + str(WARNING_SIGNS_LIMIT) + ")",
                "Allais paradox (Q7 and Q8)",
                "Possible framing effect (Q9 ladder vs Q5)",
                "Verdict on the risk ladders",
            ],
            "Result": [
                str(len(quality["straight_lined"])) + " of 9: " + straight_text,
                yes_no(quality["negative_gamble"]),
                str(quality["warning_signs"]),
                yes_no(quality["allais"]),
                yes_no(quality["framing"]),
                verdict,
            ],
        }
    )
    return table


def make_comparison_chart(eut, bpt):
    labels = ["EUT (benchmark)", "SP/A–BPT (recommended)"]
    safe_shares = [eut["safe"] * 100, bpt["security"] * 100]
    risky_shares = [eut["equity"] * 100, bpt["aspiration"] * 100]

    figure, axis = plt.subplots(figsize=(6, 4.5))
    axis.bar(labels, safe_shares, color="tab:blue", label="Safe: debt / security layer")
    axis.bar(labels, risky_shares, bottom=safe_shares, color="tab:orange", label="Risky: equity / aspiration layer")
    for i in range(len(labels)):
        axis.text(i, safe_shares[i] / 2, "{:.1f}%".format(safe_shares[i]), ha="center", va="center", color="white", fontsize=10)
        axis.text(i, safe_shares[i] + risky_shares[i] / 2, "{:.1f}%".format(risky_shares[i]), ha="center", va="center", fontsize=10)
    axis.set_ylim(0, 100)
    axis.set_ylabel("Share of the portfolio (%)")
    axis.set_title("EUT vs SP/A–BPT portfolio")
    axis.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2)
    figure.tight_layout()
    return figure


def make_side_by_side_table(eut, bpt, initial_wealth, fall_limit):
    eut_loss = stress_loss(eut["equity"])
    bpt_loss = stress_loss(bpt["aspiration"])
    table = pd.DataFrame(
        {
            "Measure": [
                "Safe share (range)",
                "Risky share (range)",
                "Safe amount",
                "Risky amount",
                "Loss if equity falls 20%",
                "Within the fall they can sit through (Q31)?",
            ],
            "EUT (benchmark)": [
                range_text(1 - eut["equity_high"], 1 - eut["equity_low"]),
                range_text(eut["equity_low"], eut["equity_high"]),
                format_rupees(initial_wealth * eut["safe"]),
                format_rupees(initial_wealth * eut["equity"]),
                percent_text(eut_loss),
                yes_no(eut_loss <= fall_limit),
            ],
            "SP/A–BPT (recommended)": [
                range_text(bpt["security_low"], bpt["security_high"]),
                range_text(bpt["aspiration_low"], bpt["aspiration_high"]),
                format_rupees(initial_wealth * bpt["security"]),
                format_rupees(initial_wealth * bpt["aspiration"]),
                percent_text(bpt_loss),
                yes_no(bpt_loss <= fall_limit),
            ],
        }
    )
    return table


def show_quality_section(quality):
    st.header("1. Can we trust the risk answers?")
    st.write("Before building portfolios, we check whether the risk ladders (Q9 to Q19) were answered carefully. A ladder where every row has the same answer only gives a bound, not a value.")
    st.table(make_quality_table(quality))
    if not quality["reliable"]:
        st.warning("The risk ladders show " + str(quality["warning_signs"]) + " warning signs, so the fitted γ, α and λ are not used at face value. The SP/A–BPT portfolio is built from the stated-preference answers and sized conservatively.")
    if quality["framing"]:
        st.info(
            "Possible framing effect: the Q9 ladder alone gives a certainty equivalent of about "
            + format_rupees(quality["ladder_q9_ce"])
            + ", above the expected value of Rs 5,00,000, but in Q5 the investor took the sure Rs 5,00,000. The ladder only places the certainty equivalent between two rows, so this is a weak signal."
        )
    if quality["allais"]:
        st.info("Allais paradox: the investor's own choices break Expected Utility Theory, so the EUT portfolio is only a benchmark and SP/A–BPT is the operating portfolio.")


def show_eut_section(eut, fits, quality):
    st.header("2. EUT portfolio (benchmark)")
    st.write("Under CRRA utility with lognormal returns, the Merton–Samuelson rule gives the best share of wealth in equity. We use an equity risk premium of 7% and equity volatility of 20% (σ² = 0.04).")
    st.latex("w^{*} = \\frac{\\mu - r_f}{\\gamma\\,\\sigma^{2}} = \\frac{0.07}{" + "{:.3f}".format(fits["gamma"]) + " \\times 0.04}")
    if eut["raw_share"] is None:
        st.write("γ is zero or negative, so there is no finite optimum: EUT would put everything and more into equity.")
    else:
        st.write("Raw result: w* = **" + "{:.2f}".format(eut["raw_share"]) + "** (" + "{:.0%}".format(eut["raw_share"]) + " in equity).")
    if eut["capped"]:
        st.write("This is a corner solution that needs borrowing. With no leverage and the investor's own loss limits, equity is capped at **90% to 100%**. A γ this small, fitted on small stakes, is not a safe guide to large-stakes behaviour (Rabin, 2000).")
    else:
        st.write("EUT equity share: **" + "{:.0%}".format(eut["equity"]) + "**, and " + "{:.0%}".format(eut["safe"]) + " in debt.")
    if not quality["reliable"]:
        st.warning("γ is a lower bound here, so this equity share is a ceiling, not a point estimate. It is not used as the recommendation.")
    if quality["allais"]:
        st.write("Because of the Allais violation, treat this as a benchmark, not the operating allocation.")


def show_bpt_section(bpt, fear_hope, aspiration_lines, profile, quality):
    st.header("3. SP/A–BPT portfolio (recommended)")
    st.write("Following Lopes (1987) and Shefrin and Statman (2000), the portfolio is built as two mental-account layers: a **security layer** that protects a downside floor, and an **aspiration layer** that aims for the investor's target.")
    st.latex("q = \\frac{\\text{fear}}{\\text{fear} + \\text{hope}} = \\frac{" + str(fear_hope["fear"]) + "}{" + str(fear_hope["fear"]) + " + " + str(fear_hope["hope"]) + "} = " + "{:.3f}".format(fear_hope["q"]))
    st.write("Fear = Q24 'I first think about what I could lose'. Hope = Q24 'I first think about how much it could grow'. The investor is **" + fear_hope["label"].lower() + "**.")

    reasons = "Starts at the Q22 safe share (" + profile["safe_answer"].lower() + " = " + "{:.0%}".format(bpt["base_security"]) + ")"
    if bpt["extra_security"] > 0:
        reasons = reasons + ", plus " + "{:.0%}".format(bpt["extra_security"]) + " because the risk ladders are unreliable"
    reasons = reasons + ". Checked against Q21 (largest yearly loss accepted: " + "{:.0%}".format(profile["security_loss"]) + ") and Q31 (fall they can sit through: " + profile["fall_answer"] + ")."

    table = pd.DataFrame(
        {
            "Layer": ["Security", "Aspiration"],
            "Allocation": [range_text(bpt["security_low"], bpt["security_high"]), range_text(bpt["aspiration_low"], bpt["aspiration_high"])],
            "Composition": [security_composition(), " ".join(aspiration_lines)],
        }
    )
    st.table(table)
    st.write("**How the security layer is sized:** " + reasons)
    st.caption("Charts and rupee amounts use the middle of each range.")


def save_portfolios(portfolios):
    st.session_state["portfolios"] = portfolios
    if "client_id" in st.session_state:
        values = {
            "eut_equity": portfolios["eut"]["equity"],
            "bpt_security": portfolios["bpt"]["security"],
            "bpt_aspiration": portfolios["bpt"]["aspiration"],
            "data_reliable": portfolios["quality"]["reliable"],
        }
        update_response_row(st.session_state["client_id"], values)


def show_portfolio_page():
    st.title("My Portfolios")
    needed = ["profile", "quiz", "personality", "functions"]
    for key in needed:
        if key not in st.session_state:
            st.warning("Please finish the Client Profile, Risk & Time Quiz, Personality and My Utility & Value pages first.")
            return

    profile = st.session_state["profile"]
    results = st.session_state["quiz"]["results"]
    answers = st.session_state["quiz"]["answers"]
    traits = st.session_state["personality"]["traits"]
    fits = st.session_state["functions"]
    portfolios = build_portfolios(profile, results, answers, traits, fits)
    save_portfolios(portfolios)

    st.write("Portfolios for an investable amount of **" + format_rupees(profile["initial_wealth"]) + "**, split between a safe asset (debt) and a risky asset (broad equity).")
    show_quality_section(portfolios["quality"])
    show_eut_section(portfolios["eut"], fits, portfolios["quality"])
    show_bpt_section(portfolios["bpt"], portfolios["fear_hope"], portfolios["aspiration_lines"], profile, portfolios["quality"])

    st.header("4. Side by side")
    left_column, right_column = st.columns([1, 1])
    with left_column:
        st.table(make_side_by_side_table(portfolios["eut"], portfolios["bpt"], profile["initial_wealth"], portfolios["fall_limit"]))
        st.write("**Recommendation:** use the SP/A–BPT portfolio. The EUT portfolio is shown as a benchmark of what strict Expected Utility Theory implies from the fitted γ.")
    with right_column:
        figure = make_comparison_chart(portfolios["eut"], portfolios["bpt"])
        st.pyplot(figure)
        plt.close(figure)
