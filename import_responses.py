import pandas as pd


EXCEL_FILE = "docs/Investor Preference Questionnaire — MBA680 (Responses).xlsx"
OUTPUT_FILE = "data/investor_responses.csv"

TABLE_ROWS = {
    "q9": 5,
    "q10": 5,
    "q11": 5,
    "q12": 5,
    "q13": 5,
    "q14": 5,
    "q15": 5,
    "q18": 5,
    "q19": 5,
    "q24": 5,
    "q25": 8,
}


def add_table_columns(names, key):
    for row_number in range(1, TABLE_ROWS[key] + 1):
        names.append(key + "_" + str(row_number))


def make_column_names():
    names = ["timestamp", "name", "q2", "q3", "q4", "q5", "q6", "q7", "q8"]
    for key in ["q9", "q10", "q11", "q12", "q13", "q14", "q15"]:
        add_table_columns(names, key)
    names.append("q16")
    names.append("q17")
    add_table_columns(names, "q18")
    add_table_columns(names, "q19")
    for key in ["q20", "q21", "q22", "q23"]:
        names.append(key)
    add_table_columns(names, "q24")
    add_table_columns(names, "q25")
    for key in ["q26", "q27", "q28"]:
        names.append(key)
    for item_number in range(1, 16):
        names.append("bfi_" + str(item_number))
    for key in ["q31", "q32", "q33", "q34"]:
        names.append(key)
    return names


def main():
    responses = pd.read_excel(EXCEL_FILE)
    column_names = make_column_names()
    if len(responses.columns) != len(column_names):
        print("The sheet has", len(responses.columns), "columns but we expected", len(column_names))
        return
    responses.columns = column_names
    responses = responses.sort_values("timestamp").reset_index(drop=True)

    investor_ids = []
    for i in range(len(responses)):
        investor_ids.append("INV-" + str(i + 1).zfill(2))
    responses.insert(0, "investor_id", investor_ids)
    responses = responses.drop(columns=["timestamp", "name"])

    responses.to_csv(OUTPUT_FILE, index=False)
    print("Saved", len(responses), "investors to", OUTPUT_FILE)


main()
