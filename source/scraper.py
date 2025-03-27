from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from arbitrage_calculator import calculate_arbitrage

with open("../betting_accounts/TOTALS.txt", "r+") as file:
    df = pd.read_csv("arbitrage_opportunities.csv")
    profit = df["Profit"].sum()
    lines = file.readlines()
    total = float(lines[0].strip())
    new_total = round(total + profit, 2)

bet_amount = 0.1 * round(new_total)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode

url = "https://www.oddsshopper.com/tools/arbitrage/MI"

def scrapeOdds(url_in):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url_in)
    html = driver.page_source

    doc = BeautifulSoup(html, "html.parser")

    odds_divs = doc.find_all(class_="MuiBox-root css-70qvj9")
    odds = [div.text for div in odds_divs]

    sportsbooks = []
    for div in odds_divs:
        if div.img and "alt" in div.img.attrs:
            sportsbooks.append(div.img["alt"])
        else:
            sportsbooks.append(None)

    bet_name_divs = doc.find_all(class_="MuiBox-root css-pv7o2b")
    bet_names = [div.text for div in bet_name_divs]

    bet_type_divs = doc.find_all(class_="MuiDataGrid-cellContent")
    bet_types = [div["title"] for div in bet_type_divs if "title" in div.attrs]
################## HERE
    links = []
    link_divs = doc.find_all(class_="MuiButtonBase-root MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeSmall MuiButton-outlinedSizeSmall MuiButton-colorPrimary MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeSmall MuiButton-outlinedSizeSmall MuiButton-colorPrimary css-15rll5b")
    for div in link_divs:
        if "href" in div.attrs:
            links.append(div["href"])
        else:
            links.append(None)
#####################
    sides_divs = doc.find_all(class_="MuiStack-root css-wkgdg0")
    sides = [child.text for div_parent in sides_divs for child in div_parent.find_all('div', recursive=False)]

    line_divs = doc.find_all(class_="MuiStack-root css-9jay18")
    lines = []
    for div_parent in line_divs:
        for child in div_parent.find_all('div', class_="MuiBox-root css-0", recursive=False):
            lines.append(child.text)

    lines_length = len(lines)
    for index in range(int(lines_length / 2)):
        line_1, line_2 = str(lines[index * 2]), str(lines[(index * 2) + 1])
        if line_1 == "-" and line_2 == "-":
            lines[index * 2] = ""
            lines[(index * 2) + 1] = ""
        elif "o" in line_1 or "o" in line_2:
            new_line = line_1.split(" ")
            lines[index * 2] = new_line[1]
            lines[(index * 2) + 1] = new_line[1]

    final_bets = []
    for name_index, name in enumerate(bet_names):
        odds_sportsbook_index = name_index * 2
        if odds_sportsbook_index + 1 >= len(links):
            print(f"Skipping bet at index {name_index}: not enough links")
            print(len(links))
            continue

        current_bet = [
            name,
            bet_types[name_index] if name_index < len(bet_types) else None,
            sides[odds_sportsbook_index] if odds_sportsbook_index < len(sides) else None,
            lines[odds_sportsbook_index] if odds_sportsbook_index < len(lines) else None,
            sportsbooks[odds_sportsbook_index] if odds_sportsbook_index < len(sportsbooks) else None,
            odds[odds_sportsbook_index] if odds_sportsbook_index < len(odds) else None,
            sides[odds_sportsbook_index + 1] if odds_sportsbook_index + 1 < len(sides) else None,
            lines[odds_sportsbook_index + 1] if odds_sportsbook_index + 1 < len(lines) else None,
            sportsbooks[odds_sportsbook_index + 1] if odds_sportsbook_index + 1 < len(sportsbooks) else None,
            odds[odds_sportsbook_index + 1] if odds_sportsbook_index + 1 < len(odds) else None,
            links[odds_sportsbook_index],
            links[odds_sportsbook_index + 1],
        ]

        final_bets.append(current_bet)

    columns = [
        "Team/Player", "Bet Type", "Side 1", "Line 1", "Book 1", "Odds 1",
        "Side 2", "Line 2", "Book 2", "Odds 2", "Link 1", "Link 2"
    ]
    df = pd.DataFrame(final_bets, columns=columns)

    bet1_list, bet2_list, payout_list, profit_list, return_percentage_list = [], [], [], [], []

    for row in range(len(final_bets)):
        try:
            bet1, bet2, payout = calculate_arbitrage(bet_amount, int(df.iloc[row, 5]), int(df.iloc[row, 9]))
        except (TypeError, ValueError):
            bet1, bet2, payout = 0, 0, 0

        profit = payout - bet_amount
        profit_list.append(profit)
        return_percentage_list.append(round(profit / bet_amount * 100, 2) if bet_amount > 0 else 0)
        bet1_list.append(bet1)
        bet2_list.append(bet2)
        payout_list.append(payout)

    df["Bet 1"] = bet1_list
    df["Bet 2"] = bet2_list
    df["Payout"] = payout_list
    df["Profit"] = profit_list
    df["Percent Return"] = return_percentage_list

    indices_to_drop = [
        i for i in range(df.shape[0])
        if df["Bet 1"][i] == 0 or df["Bet 2"][i] == 0 or df["Payout"][i] == 0
        or df["Profit"][i] < 0 or df["Book 1"][i] in ["Rebet", "Fliff"]
        or df["Book 2"][i] in ["Rebet", "Fliff"]
    ]

    for i in range(df.shape[0]):
        if i in indices_to_drop:
            continue
        for j in range(i + 1, df.shape[0]):
            if (
                df["Team/Player"][i] == df["Team/Player"][j] and
                df["Bet Type"][i] == df["Bet Type"][j]
            ):
                indices_to_drop.append(j)

    df.drop(indices_to_drop, inplace=True)
    df = df.head(6)
    df.to_csv("arbitrage_opportunities.csv")

    return df

# Uncomment to run the function
#print(scrapeOdds(url).to_string(index=False))