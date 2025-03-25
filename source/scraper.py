from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from arbitrage_calculator import calculate_arbitrage


#print("Here"+ str(bet_amount))
# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode

url = "https://www.oddsshopper.com/tools/arbitrage/MI"

def scrapeOdds(url_in): #returns a dataframe of all the bets and information that you need for the calculator
    ##########################################################
    with open("../betting_accounts/TOTALS.txt", "r+") as file:
        lines = file.readlines()
        total = float(lines[0].strip())
    bet_amount = .03 * round(total)
    ###############################################################
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url_in)
    html = driver.page_source

    doc = BeautifulSoup(html, "html.parser")

    odds_divs = doc.find_all(class_="MuiBox-root css-70qvj9")
    odds = []
    sportsbooks = []

    for div in odds_divs:
        odds.append(div.text)
        sportsbooks.append(div.img["alt"])

    bet_name_divs = doc.find_all(class_="MuiBox-root css-pv7o2b")
    bet_names = []
    for div in bet_name_divs:
        bet_names.append(div.text)

    bet_type_divs = doc.find_all(class_="MuiDataGrid-cellContent")
    bet_types = []
    for div in bet_type_divs:
        bet_types.append(div["title"])
    
    links = []
    link_divs = doc.find_all(class_ = "MuiButtonBase-root MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeMedium MuiButton-outlinedSizeMedium MuiButton-colorPrimary MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeMedium MuiButton-outlinedSizeMedium MuiButton-colorPrimary css-1llxncn")
    for div in link_divs:
        links.append(div["href"])
    lines = []
    # "MuiStack-root arb-bet-wrapper css-1ki0w8z"
    lines_divs = doc.find_all(class_ ="MuiStack-root arb-bet-wrapper css-1ki0w8z")


    sides_divs = doc.find_all(class_="MuiStack-root css-wkgdg0") #NEW LINE
    sides = [] #NEW LINE
    for div_parent in sides_divs: #NEW LINE
        for child in div_parent.find_all('div', recursive=False): #NEW LINE
            sides.append(child.text) #NEW LINE
    

    line_divs = doc.find_all(class_="MuiStack-root css-9jay18") #NEW LINE
    lines = [] #NEW LINE
    for div_parent in line_divs: #NEW LINE
        for child in div_parent.find_all('div', class_="MuiBox-root css-0", recursive=False): #NEW LINE
            lines.append(child.text) #NEW LINE

    #clean the lines list
    lines_length = len(lines) #NEW LINE
    for index in range(int(lines_length / 2)): #NEW LINE
        line_1 = str(lines[index * 2]) #NEW LINE
        line_2 = str(lines[(index * 2) + 1]) #NEW LINE
        if line_1 == "-" and line_2 == "-": #NEW LINE
            #line is a moneyline therefore change value in list to nothing
            lines[index * 2] = "" #NEW LINE
            lines[(index * 2) + 1] = "" #NEW LINE
            continue #NEW LINE
        elif "o" in line_1 or "o" in line_2: #NEW LINE
            #line is an over under therefore change value to just the numerical value
            new_line_1 = line_1.split(" ") #NEW LINE
            lines[index * 2] = new_line_1[1] #NEW LINE
            lines[(index * 2) + 1] = new_line_1[1] #NEW LINE
            continue #NEW LINE
    #print(bet_name_divs)
    #print(links[0])


    final_bets = []
    name_index = 0
    for name in bet_names:
        odds_sportsbook_index = name_index*2
        current_bet = []
        current_bet.append(name)
        current_bet.append(bet_types[name_index])
        current_bet.append(sides[odds_sportsbook_index]) #NEW LINE
        current_bet.append(lines[odds_sportsbook_index]) #NEW LINE
        current_bet.append(sportsbooks[odds_sportsbook_index])
        current_bet.append(odds[odds_sportsbook_index])
        current_bet.append(sides[odds_sportsbook_index + 1]) #NEW LINE
        current_bet.append(lines[odds_sportsbook_index + 1]) #NEW LINE
        current_bet.append(sportsbooks[odds_sportsbook_index + 1])
        current_bet.append(odds[odds_sportsbook_index + 1])
        current_bet.append(links[odds_sportsbook_index])
        current_bet.append(links[odds_sportsbook_index +1])
        final_bets.append(current_bet)

        name_index+=1

    columns = ["Team/Player", "Bet Type", "Side 1", "Line 1", "Book 1", "Odds 1", "Side 2", "Line 2", "Book 2", "Odds 2", "Link 1", "Link 2"]
    df = pd.DataFrame(final_bets, columns=columns)
    print(f"LENGTH: {len(final_bets)}")
    bet1_list = []
    bet2_list = []
    payout_list = []
    profit_list = []
    return_percentage_list = []
    for row in range(len(final_bets)):
        try:
            bet1, bet2, payout = calculate_arbitrage(bet_amount, int(df.iloc[row, 5]), int(df.iloc[row, 9]))
        except TypeError:
            bet1, bet2, payout = (0,0,0)
        profit = payout - bet_amount
        profit_list.append(profit)
        return_percentage_list.append((round(profit/bet_amount*100, 2)))
        bet1_list.append(bet1)
        bet2_list.append(bet2)
        payout_list.append(payout)
    df["Bet 1"] = bet1_list
    df["Bet 2"] = bet2_list
    df["Payout"] = payout_list
    df["Profit"] = profit_list
    df["Percent Return"] = return_percentage_list


    indices_to_drop = []

    for i in range(df.shape[0]):
        if df["Bet 1"][i] == 0 or df["Bet 2"][i] == 0 or df["Payout"][i] == 0 or df["Profit"][i] < 0 or df["Book 1"][i] == "Rebet" or df["Book 2"][i] == "Rebet" or df["Book 1"][i] == "Fliff" or df["Book 2"][i] == "Fliff":
            indices_to_drop.append(i)
            continue
        if i < df.shape[0] - 2:
            for j in range(i + 1, df.shape[0]):
                if (df["Team/Player"][i] == df["Team/Player"][j] and df["Bet Type"][i] == df["Bet Type"][j]):
                    indices_to_drop.append(i)
                    print("Dropped line")

    df.drop(indices_to_drop, inplace=True) 
    df = df.head(6)
    df.to_csv("arbitrage_opportunities.csv")
    print(f"FINAL LENGTH: {df.shape[0]}")


    return df

#print(scrapeOdds(url).to_string(index=False))
#scrapeOdds(url)


