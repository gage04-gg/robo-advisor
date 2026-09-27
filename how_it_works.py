import pandas as pd
import streamlit as st


def show_overview():
    st.write(
        "This portal works like a robo-advisor. A client answers one questionnaire, and the portal turns the answers into "
        "a risk profile, a personality profile, a utility function and a value function, two portfolio recommendations "
        "and personal advice. It follows the six steps of our MBA680 Behavioural Finance project."
    )
    table = pd.DataFrame(
        {
            "Step": ["1", "2", "3", "4", "5", "6"],
            "Page": ["Client Profile", "Risk & Time Quiz", "Personality", "My Utility & Value", "My Portfolios", "Advice"],
            "What it measures or produces": [
                "Who the client is, how much they invest, and what counts as success or failure",
                "How the client chooses between safe and risky money, and between money now and later",
                "The client's Big Five personality traits",
                "The client's utility function (EUT) and value function (Prospect Theory)",
                "One portfolio under Expected Utility Theory and one under SP/A Behavioural Portfolio Theory",
                "How the client's personality should shape the advice",
            ],
        }
    )
    st.table(table)
    st.write("Pages 1 to 3 are the questionnaire. Pages 4 to 6 are calculated automatically from the answers. Group Results compares all investors in our peer group.")


def show_step_1():
    st.header("Step 1: Client profile")
    st.write(
        "Problem statement 1 gives every client Rs 1 crore to invest for 3 months. The questionnaire then asks what the client "
        "would call a failure (Q21) and a clear success (Q23) on Rs 10 lakh over one year, how much they want kept completely safe (Q22), "
        "and how big a fall they could sit through (Q31)."
    )
    st.write("From these we get two numbers that the behavioural portfolio uses:")
    st.markdown("- **Security level:** the wealth the client never wants to fall below.")
    st.markdown("- **Aspiration level:** the wealth the client hopes to reach.")
    with st.expander("Formulas"):
        st.latex("\\text{Security level} = W_0 \\times (1 - \\text{loss accepted in Q21})")
        st.latex("\\text{Aspiration level} = W_0 \\times (1 + \\text{return in Q23})^{T}")
        st.write("W₀ is the investable amount and T is the horizon in years.")


def show_step_2():
    st.header("Step 2: Risk and time preferences")
    st.write(
        "Most questions are **choice tables** (a 'multiple price list'). Each row is a choice between a gamble and a sure amount, "
        "and the sure amount goes up row by row. The row where the client switches from the gamble to the sure amount tells us "
        "the **certainty equivalent (CE)**: the sure amount that feels as good as the gamble. We take the midpoint of the two rows around the switch."
    )
    table = pd.DataFrame(
        {
            "Questions": ["Q5–Q6", "Q7–Q8", "Q9–Q11", "Q12", "Q13", "Q14–Q15", "Q16–Q17", "Q18–Q19", "Q24–Q28"],
            "What they tell us": [
                "Straight choices between a sure amount and a gamble",
                "The Allais paradox: whether the client's choices break Expected Utility Theory",
                "How much the client values risky gains (CE for gains)",
                "How the client behaves when facing a loss (CE for losses)",
                "Loss aversion: how big a gain is needed to accept a possible loss",
                "How the client weighs a small (5%) and a large (95%) chance",
                "Reference dependence: whether the purchase price changes how a loss feels",
                "Time preference: how much extra money is needed to wait 6 months, now and a year from now",
                "Behavioural biases such as herding, overconfidence and the disposition effect",
            ],
        }
    )
    st.table(table)
    st.write(
        "A CE below the gamble's expected value means the client prefers safety (risk averse). If a client switches back and forth "
        "in a table, the portal uses the first switch and shows a warning."
    )


def show_step_3():
    st.header("Step 3: Personality (BFI-2-XS)")
    st.write(
        "We use the 15-item Big Five Inventory-2 Extra-Short Form (Soto and John, 2017). Each statement is answered from 1 (disagree strongly) "
        "to 5 (agree strongly). Some statements are worded in the opposite direction, so they are reverse scored. Each trait is the average of its 3 statements."
    )
    table = pd.DataFrame(
        {
            "Trait": ["Extraversion", "Agreeableness", "Conscientiousness", "Negative Emotionality", "Open-Mindedness"],
            "In simple words": [
                "Sociable, assertive, energetic",
                "Kind, respectful, trusting",
                "Organised, reliable, gets things done",
                "Worries, feels low, gets upset easily",
                "Curious, creative, likes art and ideas",
            ],
        }
    )
    st.table(table)
    with st.expander("Formulas"):
        st.latex("\\text{Reverse scored item} = 6 - \\text{answer}, \\qquad \\text{Trait score} = \\frac{\\text{sum of its 3 items}}{3}")
        st.write("A score of 3.5 or more is High, 2.5 or less is Low, anything in between is Medium.")


def show_step_4():
    st.header("Step 4: Utility and value functions")
    st.subheader("Expected Utility Theory (EUT) with CRRA utility")
    st.write(
        "Traditional finance assumes people choose the option with the highest expected utility of their total wealth. "
        "We use constant relative risk aversion (CRRA) utility. The bigger γ is, the more the client dislikes risk. "
        "γ is found from the coin-toss questions Q9 and Q10: we search for the γ that makes the client indifferent between the toss and their CE."
    )
    st.latex("U(W) = \\frac{W^{1-\\gamma}}{1-\\gamma}, \\qquad U(W_0 + CE) = 0.5\\,U(W_0 + X) + 0.5\\,U(W_0)")
    st.subheader("Prospect Theory value function")
    st.write(
        "Kahneman and Tversky showed that people judge gains and losses from a reference point, not total wealth, "
        "and that losses hurt more than equal gains please. The value function is S-shaped with a kink at zero."
    )
    st.latex("v(x) = x^{\\alpha} \\;(x \\ge 0), \\qquad v(x) = -\\lambda(-x)^{\\beta} \\;(x < 0)")
    st.markdown("- **α** (from Q11): how quickly the pleasure of gains levels off.")
    st.markdown("- **β** (from Q12): how quickly the pain of losses levels off.")
    st.markdown("- **λ** (from Q13): loss aversion. λ above 1 means losses hurt more than gains.")
    with st.expander("Probability weighting and time preference"):
        st.write("From Q14 and Q15 we fit how the client weighs small and large chances (Tversky and Kahneman, 1992):")
        st.latex("w(p) = \\frac{p^{c}}{\\left(p^{c} + (1-p)^{c}\\right)^{1/c}}")
        st.write("From Q18 and Q19 we fit the β–δ model of time preference. β below 1 means present bias: money today gets an extra premium.")
        st.latex("\\delta = \\frac{1}{1 + r_{later}}, \\qquad \\beta = \\frac{1}{(1 + r_{now})\\,\\delta}")


def show_step_5():
    st.header("Step 5: Portfolios")
    st.write("Each portfolio is split between a safe asset (debt) and a risky asset (broad equity).")
    st.subheader("First: can we trust the answers?")
    st.write(
        "The portal checks for tables where every row got the same answer, for accepting a gamble that loses money on average, "
        "and for the Allais paradox. With 4 or more warning signs, the fitted numbers are not trusted and the portfolio is built more conservatively."
    )
    st.subheader("EUT portfolio (benchmark)")
    st.write(
        "The Merton–Samuelson rule gives the best share in equity for a CRRA investor. We assume an equity risk premium of 7% "
        "and volatility of 20%. There is no borrowing, so the share is capped at 90% to 100% if the formula asks for more."
    )
    st.latex("w^{*} = \\frac{\\mu - r_f}{\\gamma\\,\\sigma^{2}}")
    st.subheader("SP/A–BPT portfolio (recommended)")
    st.write(
        "Behavioural Portfolio Theory (Shefrin and Statman, 2000) builds on Lopes' SP/A theory: people balance **Security**, **Potential** "
        "and **Aspiration**, pulled between fear and hope. So the portfolio is built as two mental-account layers:"
    )
    st.markdown("- **Security layer:** safe assets that protect a downside floor. Sized from Q22, with extra safety if the answers are unreliable.")
    st.markdown("- **Aspiration layer:** equity that aims for the client's target. What goes in it depends on personality and biases.")
    st.latex("q = \\frac{\\text{fear}}{\\text{fear} + \\text{hope}}")
    st.write("q above 0.5 means the client is fear-dominant, below 0.5 hope-dominant (from Q24).")
    st.write(
        "Because real investors think in layers and often break EUT (for example, the Allais paradox), the SP/A–BPT portfolio is our recommendation. "
        "The EUT portfolio is shown as a benchmark."
    )


def show_step_6():
    st.header("Step 6: Personality-based advice")
    st.write(
        "Personality traits are stable, while answers to risk questions can be affected by framing, fatigue or careless answering. "
        "So the portal uses personality as a check on the numbers and as a guide to how the advice should be given."
    )
    st.info(
        "**General principle:** where personality and behaviour agree, that is strong evidence. Where they disagree, "
        "for example a client who says they are calm but would sell everything in a fall, the portfolio follows the behaviour."
    )
    table = pd.DataFrame(
        {
            "Signal": [
                "Low Negative Emotionality but sells everything in a fall",
                "High Conscientiousness and holds through falls",
                "Low Open-Mindedness",
                "Low Agreeableness",
                "High Agreeableness",
                "Strong herding or overconfidence",
                "High monitoring anxiety and high loss aversion",
            ],
            "Advice": [
                "Name the gap to the client; size safety from the drawdown answer",
                "Trust the client's plan adherence",
                "Keep equity in familiar large-cap or index funds",
                "Explain the reasoning, not just the recommendation",
                "Actively ask about disagreements",
                "Fewer holdings and rule-based rebalancing",
                "Quarterly instead of daily statements",
            ],
        }
    )
    st.table(table)


def show_privacy_and_limits():
    st.header("Privacy and limitations")
    st.markdown("- Peer-group investors are shown only as INV-01, INV-02 and INV-03. Names are removed when the survey is imported.")
    st.markdown("- Each preference comes from a 5-row table, so it is only known to lie between two rows.")
    st.markdown("- The utility fit assumes background wealth of Rs 10 lakh, and the portfolios assume a 7% equity premium and 20% volatility.")
    st.markdown("- Answers are kept only for the current browser session. Refreshing the page clears them.")


def show_references():
    with st.expander("References"):
        st.markdown("- Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. Quarterly Journal of Economics.")
        st.markdown("- Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. Econometrica.")
        st.markdown("- Lopes, L. L. (1987). Between hope and fear: The psychology of risk. Advances in Experimental Social Psychology.")
        st.markdown("- Merton, R. C. (1969). Lifetime portfolio selection under uncertainty. Review of Economics and Statistics.")
        st.markdown("- Shefrin, H., & Statman, M. (2000). Behavioral portfolio theory. Journal of Financial and Quantitative Analysis.")
        st.markdown("- Soto, C. J., & John, O. P. (2017). Short and extra-short forms of the Big Five Inventory-2. Journal of Research in Personality.")
        st.markdown("- Tversky, A., & Kahneman, D. (1992). Advances in prospect theory. Journal of Risk and Uncertainty.")


def show_how_it_works_page():
    st.title("How It Works")
    show_overview()
    show_step_1()
    show_step_2()
    show_step_3()
    show_step_4()
    show_step_5()
    show_step_6()
    show_privacy_and_limits()
    show_references()
