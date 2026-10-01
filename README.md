#  Robo-Advisor
**Live app:** [gage-robo-advisor.streamlit.app](https://gage-robo-advisor.streamlit.app/)
If it shows a sleep screen, click "Yes, get this app back up!" and wait about 30 seconds.
A Streamlit web app that works like a robo-advisor. A client answers one questionnaire, and the app turns the answers into a risk profile, a personality profile, a utility function, a value function, two portfolio recommendations and personal advice.

This was a group project for the Behavioural Finance course (MBA680) at IIT Kanpur. My part was designing the risk and time-preference questionnaire and building the whole portal. It is a course project, not real investment advice.

## Why I built this

Most robo-advisors ask a few questions and put you in a "conservative", "balanced" or "aggressive" bucket. But people don't think about risk in one simple way. Many feel losses much more than gains, overweight small chances, or want part of their money completely safe while taking big risks with the rest. I wanted a tool that measures these things from a person's own answers and gives advice that fits how they actually think.

## What the app does

The app has 8 pages:

| Section | Page | What it shows |
| --- | --- | --- |
| Questionnaire | Client Profile | Investable amount, horizon, what counts as failure (security level) and success (aspiration level) |
| Questionnaire | Risk & Time Quiz | Choice tables between sure amounts and gambles, and between money now and later |
| Questionnaire | Personality | Big Five personality traits (15-item BFI-2-XS) |
| My Results | My Utility & Value | Fitted utility function (Expected Utility Theory) and value function (Prospect Theory) |
| My Results | My Portfolios | An EUT benchmark portfolio and a behavioral SP/A portfolio |
| My Results | Advice | Personal advice based on personality and biases |
| Reports | Group Results | All investors in our peer group side by side |
| Help | How It Works | Every formula and step in plain language |

## How it works

**1. Measuring risk attitude.** Most questions are choice tables. Each row offers a gamble or a sure amount, and the sure amount goes up row by row. The row where the client switches gives the certainty equivalent (CE): the sure amount that feels as good as the gamble.

**2. Fitting the client's preferences from their answers.**
- Risk aversion (γ) for a CRRA utility function, solved from the CE
- Prospect Theory: curvature for gains (α) and losses (β), and loss aversion (λ)
- Probability weighting: whether the client overweights small chances (Tversky–Kahneman function)
- Time preference: patience and present bias (β–δ model)
- Behavioral biases such as the Allais paradox, the disposition effect, herding and overconfidence

**3. Building two portfolios.**
- **EUT benchmark:** equity share = (μ − r_f) / (γσ²), with no borrowing or short selling
- **SP/A behavioral portfolio (recommended):** a security layer the client never wants to lose, plus an aspiration layer for growth, sized from the client's own answers

**4. Checking data quality.** If a client gives the same answer in every row of many tables, or accepts a gamble that loses money on average, the app flags the answers as unreliable and adds a bigger safety layer (+20 percentage points) to their portfolio.

**5. Personality-based advice.** Fixed rules turn the Big Five scores and bias signals into advice, for example sticking to broad index funds for less open-minded clients, or rule-based rebalancing for overconfident ones.

## Results for our peer group

We ran the questionnaire with 3 peer investors.

| Investor | Security layer | Aspiration layer | Data-quality warnings |
| --- | --- | --- | --- |
| INV-01 | 25–30% | 70–75% | 0 |
| INV-02 | 45–50% | 50–55% | 7 (flagged as unreliable) |
| INV-03 | 50–55% | 45–50% | 1 |

INV-02 took the sure amount in almost every row, so their answers could not show their real risk attitude. The app flagged this and gave them a larger safety layer.

## Data and privacy

The survey responses came from a Google Form. `import_responses.py` converts them once into `data/investor_responses.csv`. This step **removes names and timestamps** and gives each person an ID (INV-01, INV-02, INV-03). The original file with names is listed in `.gitignore` and is never uploaded.

## Assumptions

Every modelling choice is written down in [`assumptions.md`](assumptions.md): how each question is scored, how each parameter is solved, and which numbers are our own assumptions (for example, a 7% equity risk premium and 20% equity volatility).

## How to run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Pick an investor (INV-01 to INV-03) from the sidebar, or choose "New client" to fill in the questionnaire yourself.

## Files

| File | What it does |
| --- | --- |
| `app.py` | Starts the app and sets up the pages |
| `profile_page.py` | Client profile, security and aspiration levels |
| `risk_quiz.py` | Risk and time questionnaire and scoring |
| `personality.py` | Big Five scoring |
| `functions_fit.py` | Fits the utility, value, weighting and time functions |
| `portfolio.py` | EUT and SP/A portfolios, data-quality check, stress check |
| `advice.py` | Personality-based advice rules |
| `group_results.py` | Peer group comparison |
| `how_it_works.py` | The explanation page |
| `investors.py` | Loads the saved peer investors |
| `import_responses.py` | Converts the survey responses and removes names |

## Limitations

- Only 3 investors, so this is a product and modelling project, not a statistical study.
- Many scoring rules are our own assumptions, written down in `assumptions.md`.
- Portfolios use simple assumed market numbers, not live data.

## Tools

Python, Streamlit, pandas, NumPy, SciPy, Matplotlib
