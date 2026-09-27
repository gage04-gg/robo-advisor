# Assumptions

Every assumption made while building the portal. This list goes into the report.

The portal uses the group's questionnaire, "Investor Preference Questionnaire — MBA680" (34 questions, Google Form), word for word. Question numbers below (Q1 to Q34) are the form's numbers.

## Where each question appears in the portal

| Portal page | Form sections | Questions |
|---|---|---|
| Client Profile | About you; What counts as success or failure; What you would want held | Q1–Q4, Q21–Q24, Q31–Q34 |
| Risk & Time Quiz | Choices between risky options; Coin toss or guaranteed money; Gains and losses; Two lotteries; Money now or money later; How you tend to behave | Q5–Q20, Q25–Q28 |
| Personality | A few things about you (BFI-2-XS) | Q29–Q30 |

Each form section is kept whole on one page. Sections were grouped by purpose, so the page order is not exactly the form order.

## Phase 1: Client profile

1. Problem statement 1 gives an initial corpus of ₹1 crore and a 3-month investment period (ending 24 November). These are the defaults for "Investable amount" and "Investment horizon" (0.25 years). They are not in the questionnaire, and the client can change them.
2. Q4 (the horizon the client would want for ₹10 lakh) is recorded, but the portfolio uses the PS1 horizon.
3. **Security level (Q21).** Q21 is asked for ₹10 lakh over one year. We read it as the largest loss the client accepts: 0%, 5%, 10%, 20%, and 30% for "Below Rs 8,00,000 is still acceptable" (our assumption). Security level = investable amount × (1 − loss). The loss floor is **not** scaled down for a shorter horizon.
4. **Aspiration level (Q23).** Q23 gives a yearly return: 5%, 10%, 20%, 30%, and 50% for "Rs 15,00,000 or more" (our assumption). Aspiration level = investable amount × (1 + return)^horizon in years. For 3 months at 20% a year, this is ₹1 crore × 1.2^0.25 = ₹1,04,66,351.
5. **Safe share (Q22)** is stored as 0%, 25%, 50%, 75%, and 90% for "Almost all of it" (our assumption).
6. Q24 statements are labelled: loss focus, gain focus, certainty preference, mental accounting, layered (BPT) thinking.
7. Q31–Q34 (tolerable fall, number of stocks, overall approach, exclusions) are recorded for Phases 5 and 6.
8. The questionnaire does not ask for age, a written goal, or an acceptable chance of missing the aspiration level, so the portal no longer asks for them.
9. Each saved profile gets a client ID (the date and time it was saved). Quiz and personality results are added to the same row of `data/responses.csv`.

## Phase 2: Risk and time questionnaire

10. **Switch point.** In each table, the switch point is the first row where the person picks the "switch" column: the guarantee in Q9–Q11 and Q14–Q15, the coin toss in Q12, "Agree to toss" in Q13, and "Wait" in Q18–Q19.
11. **Certainty equivalent (Q9–Q12, Q14, Q15).** CE = midpoint of the two amounts around the switch. If the switch is in row 1, CE = midpoint of ₹0 and the row-1 amount. If the person never switches, CE = the last amount shown, and we note that the true CE is at least this.
12. In Q12, the CE is a loss (negative). A person who accepts small sure losses and tosses the coin for big ones switches "to the toss".
13. **Q13 mixed gamble.** L = ₹50,000. The smallest accepted G is recorded (not a midpoint). If every toss is refused, G = ₹3,00,000 is used (our assumption).
14. **Q14 and Q15.** The CE is compared with the expected value (₹25,000 and ₹4,75,000). CE above EV at 5% suggests overweighting of small probabilities; CE below EV at 95% suggests underweighting of large ones.
15. **Q5–Q8.** Q5 is a fair bet, so choosing the certain amount shows risk aversion. Q6 gives up ₹50,000 of expected value for certainty. Q7 and Q8 form an Allais pair: "certain" in Q7 plus "10% of ₹25 lakh" in Q8 is the Allais paradox (certainty effect).
16. **Q16 and Q17 (reference point).** Feelings are scored from 1 (very negative) to 5 (very positive). Reference dependence = Q17 score minus Q16 score (the final price is the same, only the purchase price differs).
17. **Q18 and Q19 (time).** Indifference amount = midpoint of the two later amounts around the switch (row 1 uses the midpoint of ₹50,000 and ₹52,000; "never waits" uses ₹72,000, noted as "at least"). 6-month rate = amount / ₹50,000 − 1. Monthly rate = (1 + 6-month rate)^(1/6) − 1. Yearly rate = (1 + monthly rate)^12 − 1. Present bias if the Q18 rate is above the Q19 rate.
18. **Q25 statements** are labelled: house money effect, herding, family influence, conservatism, confirmation bias, disposition effect, overconfidence, myopic loss aversion. A score of 4 or 5 is a "strong" signal, 1 or 2 "weak".
19. **Q28.** Selling the winner ("The one that is up") is read as a sign of the disposition effect.
20. **Inconsistent answers.** A person is inconsistent in a table if they go back to the first column after switching. We use their first switch and show a warning.

## Phase 3: Personality (BFI-2-XS)

21. Personality is measured with the 15-item BFI-2 Extra-Short Form (Soto & John, 2017), as used in the questionnaire (Q29 has items 1–8, Q30 has items 9–15).
22. Each BFI-2-XS item is word for word an item of the full BFI-2. Its trait and reverse keying were taken from the official BFI-2 scoring key (Colby Personality Lab). This gives Extraversion 1R, 6, 11; Agreeableness 2, 7R, 12; Conscientiousness 3R, 8R, 13; Negative Emotionality 4, 9, 14R; Open-Mindedness 5, 10R, 15. The file is `data/bfi2_items.csv`.
23. Reverse-keyed items are scored as 6 minus the answer. Each trait score is the mean of its 3 items. The XS form has only one item per facet, so facet scores are not reported.
24. A trait is "High" if its score is 3.5 or more, "Low" if 2.5 or less, and "Medium" otherwise.

## Phase 4: Utility and value functions (PS Step 4)

The Step 4 questionnaire is made of questions already in our form: Q9–Q10 (utility), Q11–Q13 (value function), Q14–Q15 (probability weighting), Q5–Q6 (check), and Q18–Q19 (time preference). No new questions were added.

25. **EUT utility is CRRA over total wealth**: U(W) = W^(1−γ)/(1−γ), or ln W when γ = 1.
26. **Background wealth W₀ = ₹10,00,000.** The questionnaire frames the client's money as ₹10 lakh (Q4, Q21–Q23), so each coin toss is added to ₹10 lakh. A background wealth is needed because the tosses pay ₹0 on tails, and CRRA utility of zero wealth is not defined for γ ≥ 1. A different W₀ gives a different γ.
27. γ is solved by bisection from U(W₀ + CE) = 0.5·U(W₀ + X) + 0.5·U(W₀), separately for Q9 (X = ₹10 lakh) and Q10 (X = ₹5 lakh). The client's γ is the **average** of the two. The search range is −20 to 100; every possible answer in the form falls inside it.
28. The CLAUDE.md brief said to solve γ at the two rows around the switch and take the midpoint. We instead solve γ once at the CE (which is already the midpoint of those two rows). This keeps the method the same as for α and β.
29. Q5 and Q6 are not used to fit γ. They are a check: the page shows whether the fitted γ predicts the same choice.
30. **Prospect Theory value function**: v(x) = x^α for gains, v(x) = −λ(−x)^β for losses. The reference point is zero change in wealth.
31. **Decision weight at p = 0.5 is taken as 0.5** (linear weighting) when fitting α, β and λ, as in the project brief.
32. α comes from Q11: α = ln 0.5 / ln(CE / ₹1 lakh). β comes from Q12: β = ln 0.5 / ln(|CE| / ₹1 lakh).
33. **λ = G^α / L^β with G and L in ₹ lakh** (Q13: L = 0.5). When α ≠ β, the value of λ depends on the unit of money. We use ₹ lakh because Q11 and Q12 are in units of ₹1 lakh. The simple ratio G / L (the λ you get if α = β = 1) is also shown.
34. **Probability weighting** (an addition to the brief, since Q14 and Q15 allow it). Observed weight w(p) = (CE / X)^α at p = 0.05 (Q14) and p = 0.95 (Q15). One parameter c of the Tversky–Kahneman (1992) function w(p) = p^c / (p^c + (1−p)^c)^(1/c) is fitted by a grid search from 0.20 to 2.00 in steps of 0.01, using least squares. The same c is used for gains only; the form has no small-probability loss question.
35. The weighting fit uses α from Q11, which itself assumes w(0.5) = 0.5. The fitted c gives w(0.5) slightly below 0.5, so the two steps are not perfectly consistent. We accept this simplification.
36. **Time preference (β–δ model)**, using the monthly rates from Q18 and Q19: δ = 1 / (1 + r_later), β = 1 / ((1 + r_now)·δ). Present bias if β < 1.
37. Utility charts show utility scaled from 0 to 1 over gains of ₹0 to ₹10 lakh. This is allowed because utility is unique only up to a positive linear transformation, so scaling does not change any decision.

## Survey responses of the peer group

38. The group's Google Form responses (`docs/Investor Preference Questionnaire — MBA680 (Responses).xlsx`) are converted once by `import_responses.py` into `data/investor_responses.csv`. The conversion **drops names and timestamps** and gives each investor an ID in order of submission: INV-01, INV-02, INV-03. The portal reads only the anonymised CSV. The Excel file with names is listed in `.gitignore`, so it is never uploaded.
39. Every investor is given the PS1 settings: ₹1 crore to invest and a 0.25-year horizon.
40. INV-02 left Q2 (investment experience) blank. It is shown as "Not answered" and is not used in any calculation.
41. **Q5 is used as an extra row of Q9.** Q5 offers the same coin toss as Q9 (50% of ₹10 lakh) against a sure ₹5 lakh, so it is placed between the ₹4.5 lakh and ₹6 lakh rows of Q9 before finding the switch point. This narrows the CE. If Q5 disagrees with the Q9 rows, it is flagged as inconsistent. Because Q5 is now used in the fit, only Q6 is kept as the out-of-sample check of γ.
42. When a person takes the guarantee in the very first row (INV-02 in Q9, Q10, Q11 and Q14), the CE is below every amount shown and we use half of the first amount. Their γ is then a lower bound: the true value may be even higher.

## Phase 5: Portfolios (PS Step 5)

Method from the group's document "MBA680 Steps 5–6: Behavioural Portfolio Analysis". The portal turns its reasoning into fixed rules so the same method works for any new client. Portfolios are split between one safe asset (debt) and one risky asset (broad equity); no stock-level price data is used.

43. **EUT portfolio (benchmark).** Merton–Samuelson share in equity: w* = (μ − r_f) / (γ·σ²), with an equity risk premium of 7% and equity volatility of 20% (σ² = 0.04), using γ from Step 4.
44. No borrowing and no short selling. If w* is above 100%, or γ ≤ 0 (no finite optimum), equity is capped at **90% to 100%** (the group's recommendation for INV-01). The middle of the range (95%) is used in charts.
45. **Data-quality check.** A risk ladder is "straight-lined" if every row has the same answer (switch in row 1, or never switched). Warning signs = number of straight-lined ladders out of the nine (Q9–Q15, Q18, Q19) + 1 if the investor accepted a negative expected value gamble in Q13 (smallest accepted gain below the ₹50,000 loss). **4 or more warning signs = unreliable.** INV-02 has 7 (6 straight-lined ladders + the negative-EV gamble); INV-01 has 0; INV-03 has 1.
46. When the ladders are unreliable, the EUT share is shown as a ceiling only, and the SP/A security layer gets **20 extra percentage points** (the group's conservative sizing for INV-02).
47. **SP/A–BPT portfolio (recommended).** Security layer = Q22 safe share (0%, 25%, 50%, 75%, 90%), plus 20 points if the ladders are unreliable, given as a 5-point range [start, start + 5%]. The start is capped at 95%. Aspiration layer = the rest. Charts and rupee amounts use the middle of each range. This reproduces the group's layers exactly: INV-01 25–30% / 70–75%, INV-02 45–50% / 50–55%, INV-03 50–55% / 45–50%.
48. **Fear/hope parameter** (Lopes, 1987): q = fear / (fear + hope), where fear = Q24 "I first think about what I could lose" and hope = Q24 "I first think about how much it could grow". q > 0.5 is fear-dominant, q < 0.5 hope-dominant. It is reported with the portfolio but does not change the layer sizes.
49. **Aspiration-layer composition rules.** Open-Mindedness below 3 → familiar large-cap or broad-index equity only; 3 or more → broad index plus a modest international or thematic satellite. If the ladders are reliable and the CE is below the expected value in both Q14 (5%) and Q15 (95%) → no concentrated single-stock or lottery-like bets. Overconfidence 5/5 → a small number of holdings with rule-based rebalancing.
50. **Possible framing effect** (Q9 ladder vs Q5): flagged when the Q9 ladder alone (without the Q5 row) gives a CE above ₹5,00,000 but the investor took the sure ₹5,00,000 in Q5. The ladder only places the CE between two rows, so this is a weak signal.
51. **Stress check.** Loss in a 20% equity fall = risky share × 20%, compared with the Q31 answer (under 10% → 10%, 10–20% → 20%, 20–30% → 30%, more than 30% → no limit). It is shown for information and does not change the allocation.
52. The SP/A–BPT portfolio is the recommendation for every investor. The EUT portfolio is a benchmark of what strict Expected Utility Theory implies.

## Phase 6: Personality-based advice (PS Step 6)

53. The advice rules come from the group's Step 6 commentary. Trait levels: High ≥ 3.5, Low ≤ 2.5. The rules are:
    - **Negative Emotionality ≤ 2.5 and "Sell everything" in Q26 or Q27** → name the self-report vs behaviour gap, and size the security layer from the drawdown answer. (NE ≥ 3.5 → expect stress in falls; this direction is our extension for new clients.)
    - **Conscientiousness ≥ 3.5 and "Hold" or "Buy more" in both Q26 and Q27** → trait and behaviour agree (plan adherence); extra weight if the ladders are unreliable. (C ≤ 2.5 → automatic SIP and rebalancing, from the original brief.)
    - **Open-Mindedness < 3** → familiar large-cap equity only. **≥ 3** → international or thematic exposure is fine, but no concentrated skewed bets if the investor underweights both small and large chances.
    - **Agreeableness < 3** → lead with the reasoning. **≥ 3.5** → the client may over-defer, so the advisor should surface disagreements.
    - **Herding or family influence ≥ 4 (Q25)** → check tips against the plan.
    - **Overconfidence = 5 (Q25)** → structural limits: fewer holdings, mechanical rebalancing.
    - **Sells the winner in Q28 and disposition ≥ 4 (Q25)** → pre-committed rebalancing rules.
    - **Monitoring anxiety = 5 (Q25) and λ > 1.5** → myopic loss aversion: quarterly statements.
    - **Possible framing effect and Agreeableness < 3** → agree rebalancing bands in advance.
    - **Unreliable ladders** → trust revealed behaviour; **Allais paradox** → Prospect Theory / SP/A is the defensible model.
54. The present-bias rule from the original brief is not used, because the group's commentary does not include it.
