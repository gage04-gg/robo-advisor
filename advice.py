import pandas as pd
import streamlit as st

from personality import TRAITS, level_text
from portfolio import build_portfolios, underweights_both_chances


HIGH_SCORE = 3.5
LOW_SCORE = 2.5
LOW_AGREEABLENESS = 3.0
LOW_OPEN_MINDEDNESS = 3.0
STRONG_BIAS = 4
VERY_STRONG_BIAS = 5
HIGH_LOSS_AVERSION = 1.5

HOLDING_ANSWERS = ["Hold", "Buy more"]


def score_text(trait, traits):
    score = traits[trait]
    return trait + " " + "{:.2f}".format(score) + " (" + level_text(score) + ")"


def holds_through_falls(results):
    return results["q26_answer"] in HOLDING_ANSWERS and results["q27_answer"] in HOLDING_ANSWERS


def sells_everything(results):
    return results["q26_answer"] == "Sell everything" or results["q27_answer"] == "Sell everything"


def negative_emotionality_advice(traits, results):
    score = traits["Negative Emotionality"]
    evidence = score_text("Negative Emotionality", traits) + "; Q26: " + results["q26_answer"] + "; Q27: " + results["q27_answer"]
    if score <= LOW_SCORE and sells_everything(results):
        text = (
            "Says they are emotionally stable, but would sell everything after a 20% fall. "
            "Self-reported calm describes how they think they would feel; the drawdown answer shows what they would actually do. "
            "Size the security layer from the drawdown answer (Q31), not from the personality score, and name this gap to the client directly."
        )
        return {"theme": "Negative Emotionality: self-report vs behaviour", "evidence": evidence, "advice": text}
    if score >= HIGH_SCORE:
        text = (
            "High Negative Emotionality: expect stress and a pull to sell in market falls. "
            "Keep the security layer sized from the drawdown answer (Q31), and agree in advance what to do in a fall."
        )
        return {"theme": "Negative Emotionality", "evidence": evidence, "advice": text}
    return None


def conscientiousness_advice(traits, results, quality):
    score = traits["Conscientiousness"]
    evidence = score_text("Conscientiousness", traits) + "; Q26: " + results["q26_answer"] + "; Q27: " + results["q27_answer"]
    if score >= HIGH_SCORE and holds_through_falls(results):
        text = "Trait and behaviour agree: a conscientious investor who holds through both a market-wide and a stock-specific fall. This points to real plan adherence (Nicholson et al., 2005)."
        if not quality["reliable"]:
            text = text + " Because the risk ladders are unreliable, this is one of the few clean signals and should carry extra weight in the advice."
        return {"theme": "Conscientiousness: plan adherence", "evidence": evidence, "advice": text}
    if score <= LOW_SCORE:
        text = "Low Conscientiousness: set up automatic monthly investing (SIP) and automatic rebalancing, so the plan does not depend on remembering to act."
        return {"theme": "Conscientiousness", "evidence": evidence, "advice": text}
    return None


def open_mindedness_advice(traits, results, quality):
    score = traits["Open-Mindedness"]
    evidence = score_text("Open-Mindedness", traits)
    if score < LOW_OPEN_MINDEDNESS:
        text = (
            "Keep the aspiration layer in familiar large-cap or broad-index equity. "
            "A thematic or alternative fund would not really diversify risk; it would add a second source of worry."
        )
        return {"theme": "Open-Mindedness: asset-class familiarity", "evidence": evidence, "advice": text}
    text = "The aspiration layer can carry international, thematic or alternative exposure without much behavioural cost."
    if quality["reliable"] and underweights_both_chances(results):
        text = text + " But it should not be concentrated in single-name, highly skewed bets, given how this investor weighs small and large chances (Q14, Q15)."
    return {"theme": "Open-Mindedness: asset-class familiarity", "evidence": evidence, "advice": text}


def agreeableness_advice(traits):
    score = traits["Agreeableness"]
    evidence = score_text("Agreeableness", traits)
    if score < LOW_AGREEABLENESS:
        text = (
            "Lead the advice with the reasoning, not just the recommendation. "
            "A low-agreeableness client is more likely to push back on instructions without a justification, and to act alone if not persuaded."
        )
        return {"theme": "Agreeableness: the advisory relationship", "evidence": evidence, "advice": text}
    if score >= HIGH_SCORE:
        text = (
            "A high-agreeableness client may agree to a recommendation even when it does not fit their own stated tolerance. "
            "The advisor should actively ask about disagreements the client may not raise on their own."
        )
        return {"theme": "Agreeableness: the advisory relationship", "evidence": evidence, "advice": text}
    return None


def herding_advice(results):
    herding = results["q25_Herding"]
    family = results["q25_Family influence"]
    if herding >= STRONG_BIAS or family >= STRONG_BIAS:
        evidence = "Q25 herding " + str(herding) + "/5; family influence " + str(family) + "/5"
        text = "Strong pull to follow what friends, peers and family buy. Check any tip against the written plan before acting, and do not add holdings just because others hold them."
        return {"theme": "Herding", "evidence": evidence, "advice": text}
    return None


def overconfidence_advice(traits, results):
    overconfidence = results["q25_Overconfidence"]
    if overconfidence >= VERY_STRONG_BIAS:
        evidence = "Q25 overconfidence " + str(overconfidence) + "/5; " + score_text("Extraversion", traits)
        text = (
            "Very strong overconfidence. Overconfident investors trade too much and hold losers too long (Odean, 1998). "
            "Use structural limits: fewer individual holdings and mechanical rebalancing, instead of relying on their own judgement."
        )
        return {"theme": "Overconfidence", "evidence": evidence, "advice": text}
    return None


def disposition_advice(results):
    sells_winner = results["q28_answer"] == "The one that is up"
    self_report = results["q25_Disposition effect"]
    if sells_winner and self_report >= STRONG_BIAS:
        evidence = "Q28: sells the winner; Q25 disposition " + str(self_report) + "/5"
        text = "Self-report and revealed behaviour agree: this investor sells winners and keeps losers. Use pre-committed rebalancing rules instead of discretionary trims."
        return {"theme": "Disposition effect", "evidence": evidence, "advice": text}
    return None


def myopic_loss_aversion_advice(results, fits):
    monitoring = results["q25_Myopic loss aversion"]
    if monitoring >= VERY_STRONG_BIAS and fits["lambda"] > HIGH_LOSS_AVERSION:
        evidence = "Q25 checks portfolio constantly in a fall " + str(monitoring) + "/5; λ = " + "{:.3f}".format(fits["lambda"])
        text = (
            "Textbook myopic loss aversion (Benartzi and Thaler, 1995): frequent checking plus high loss aversion creates too much demand for safety. "
            "Send quarterly rather than daily or weekly statements. Reducing review frequency is as important as the security/aspiration split."
        )
        return {"theme": "Myopic loss aversion", "evidence": evidence, "advice": text}
    return None


def framing_advice(traits, quality):
    if quality["framing"] and traits["Agreeableness"] < LOW_AGREEABLENESS:
        evidence = "Possible framing effect (Q9 vs Q5); " + score_text("Agreeableness", traits)
        text = "Likely to second-guess the plan under pressure and see the same risk differently depending on how it is presented. Agree rules-based rebalancing bands in advance."
        return {"theme": "Governance: framing", "evidence": evidence, "advice": text}
    return None


def model_choice_advice(quality):
    if not quality["reliable"]:
        evidence = str(quality["warning_signs"]) + " warning signs in the risk ladders"
        text = "The fitted utility and value parameters are not reliable, so the portfolio is built from the stated-preference answers and revealed behaviour, and advice should be checked against what the client does rather than what they say."
        return {"theme": "Which model to trust", "evidence": evidence, "advice": text}
    if quality["allais"]:
        evidence = "Allais paradox in Q7 and Q8"
        text = "The client's own choices break Expected Utility Theory, so Prospect Theory and the SP/A–BPT portfolio are the defensible model. The EUT portfolio is only a benchmark."
        return {"theme": "Which model to trust", "evidence": evidence, "advice": text}
    return None


def build_advice(profile, results, answers, traits, fits):
    portfolios = build_portfolios(profile, results, answers, traits, fits)
    quality = portfolios["quality"]
    candidates = [
        model_choice_advice(quality),
        negative_emotionality_advice(traits, results),
        conscientiousness_advice(traits, results, quality),
        open_mindedness_advice(traits, results, quality),
        agreeableness_advice(traits),
        herding_advice(results),
        overconfidence_advice(traits, results),
        disposition_advice(results),
        myopic_loss_aversion_advice(results, fits),
        framing_advice(traits, quality),
    ]
    advice_lines = []
    for item in candidates:
        if item is not None:
            advice_lines.append(item)
    return advice_lines


def make_trait_table(traits):
    scores = []
    levels = []
    for trait in TRAITS:
        scores.append("{:.2f}".format(traits[trait]))
        levels.append(level_text(traits[trait]))
    return pd.DataFrame({"Trait": TRAITS, "Score": scores, "Level": levels})


def show_advice_page():
    st.title("Advice")
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
    advice_lines = build_advice(profile, results, answers, traits, fits)
    st.session_state["advice"] = advice_lines

    st.write("Personality traits are stable dispositions, while the risk answers are task-specific and can be affected by fatigue, framing or careless answering. So we use personality as a stability check on the numbers, and as a guide to how the advice should be given.")
    left_column, right_column = st.columns([1, 2])
    with left_column:
        st.table(make_trait_table(traits))
    with right_column:
        st.info(
            "**General principle.** Where personality and behaviour agree, that is strong evidence. "
            "Where they disagree (for example, low Negative Emotionality but selling everything in a fall), the disagreement itself is the finding, "
            "and the portfolio should be built on the revealed behaviour, not the self-report."
        )

    st.header("Advice for this investor")
    for item in advice_lines:
        st.subheader(item["theme"])
        st.caption("Evidence: " + item["evidence"])
        st.write(item["advice"])
