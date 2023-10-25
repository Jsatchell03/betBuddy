import requests
from datetime import datetime
import pytz
from time import sleep
from tqdm import tqdm

tz = pytz.timezone('America/New_York')
currTime = datetime.now().astimezone(tz).replace(second=0,microsecond=0).isoformat()[:-6]
sports_response = requests.get(
    'https://api.the-odds-api.com/v4/sports', 
    params={
        # 'api_key': "b9a39f723aac9b91fb76f02b97491ef6"
        'api_key': "1cd7e4411dfa833d8b3363b034edcea4"
    }
)

# Extra data structures are for prop bet feature coming soon

sportMarkets = {
    "americanfootball_ncaaf" : ["player_1st_td", "player_last_td", "player_anytime_td"],
    "americanfootball_nfl" : ["player_1st_td", "player_last_td", "player_anytime_td"],
    "basketball_nba": ["player_double_double"],
    "basketball_wnba": ["player_double_double"],
    "basketball_ncaab": ["player_double_double"],
    "baseball_mlb" : ["pitcher_record_a_win"],
}

# class EventObj:
#   def __init__(id, sport):
#     self.id = id
#     self.sport = sport

eventList = []

if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

else: 
    unit = 50
    sport_respone = sports_response.json()
    sportList = []
    for sport in tqdm(sport_respone):
        key = sport["key"]
        odds_response = requests.get(
            f'https://api.the-odds-api.com/v4/sports/{key}/odds',
            params={
                # 'api_key': "b9a39f723aac9b91fb76f02b97491ef6",
                'api_key': "1cd7e4411dfa833d8b3363b034edcea4",
                'regions': "us",
                'markets': "h2h",
                'oddsFormat': "decimal",
                'dateFormat': "iso",
            }
        )

        if odds_response.status_code != 200:
            if odds_response.status_code != 422:
                print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
        else:
            odds_json = odds_response.json()
            for event in odds_json:
                #  if(1 > 0):
                if(event["commence_time"][:-1]  > currTime):
                    # if(sportMarkets.get(key) != None):
                    #     eventList.append(EventObj(event["id"], event["sport_key"]))
                    outcomes = []
                    bookList = []
                    oddsList = []
                    if(len(event["bookmakers"]) and len(event["bookmakers"][0]["markets"][0]["outcomes"]) >= 1):
                        for outcome in event["bookmakers"][0]["markets"][0]["outcomes"]:
                            bookList.append(event["bookmakers"][0]["title"])
                            oddsList.append(outcome["price"])
                            outcomes.append(outcome["name"])
                        for site in event["bookmakers"]:
                            for i in range(len(site["markets"][0]["outcomes"])):
                                if(len(oddsList) <= i ):
                                    oddsList.append(site["markets"][0]["outcomes"][i]["price"])
                                    bookList.append(site["title"])
                                    outcomes.append(site["markets"][0]["outcomes"][i]["name"])
                                if(site["markets"][0]["outcomes"][i]["price"] > oddsList[i]):
                                    oddsList[i] = site["markets"][0]["outcomes"][i]["price"]
                                    bookList[i] = site["title"]
                                    outcomes[i] = site["markets"][0]["outcomes"][i]["name"]
                        sum = 0
                        percentList = []
                        for i in range(len(oddsList)):
                            sum += (1/oddsList[i])
                            percentList.append(1/oddsList[i])
                        if(sum < 1):
                            print(event["home_team"].encode(encoding = 'UTF-8', errors = 'strict'), "VS.", event["away_team"].encode(encoding = 'UTF-8', errors = 'strict'))
                            for i in range(len(oddsList)):
                                bet = (unit * (percentList[i] * 100)) / (sum * 100)
                                print(bookList[i], ":",outcomes[i].encode(encoding = 'UTF-8', errors = 'strict'), oddsList[i], "$", bet)
                            print("Profit: %", (1 - sum) * 100)
                            print("")
    
            
# Check the usage quota
print('Remaining requests', odds_response.headers['x-requests-remaining'])
print('Used requests', odds_response.headers['x-requests-used'])           