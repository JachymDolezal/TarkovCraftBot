import requests
import pandas as pd

def run_query(query):
    response = requests.post('https://tarkov-tools.com/graphql', json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))


new_query = """
query {
  crafts {
    source
    duration
    rewardItems {
      quantity
      item {
        shortName
        lastLowPrice
      }
    }
    requiredItems {
      quantity
      item {
        shortName
        lastLowPrice
      }
    }
  }
}
"""

result = run_query(new_query)
# print(result)

def filterByStation(station_id,data):
    my_columns = ['station', 'name', 'output_price', 'duration', 'input_price', 'profit', 'profit_per_hour']
    df = pd.DataFrame(columns=my_columns)
    duration = 0
    for item in data["data"]["crafts"]:
        # if item["source"] == 'Booze generator level 1':
        duration = round((item["duration"]) / 60 / 60, ndigits=3)
        # for item2 in item["rewardItems"]:
        reward = item["rewardItems"]
        name_output = reward[0]["item"]["shortName"]
        input_price = 0
        quantity = reward[0]["quantity"]
        output_item = reward[0]["item"]["lastLowPrice"]
        if output_item is None:
            output_item = 0
        output_price = quantity * int(output_item)
        station_name = item["source"]
        for item2 in range(len(item["requiredItems"])):
            # print(item["requiredItems"][item2]["quantity"])
            quantity_i = item["requiredItems"][item2]["quantity"]
            print(item["requiredItems"][item2]["item"]["lastLowPrice"])
            aitem = item["requiredItems"][item2]["item"]["lastLowPrice"]
            if aitem is None:
                aitem = 0
            price_of_items = aitem * quantity_i
            input_price = input_price + price_of_items
            profit = output_price - input_price
            profit_p_hour = round(profit / duration, ndigits=3)
        df = df.append(
            pd.Series([station_name, name_output, output_price, duration, input_price, profit, profit_p_hour],
                      index=my_columns), ignore_index=True)
    return df

print(filterByStation("Nutrition unit level 1",result))
# print(filterByStation("Nutrition unit level 2",result).sort_values(by=['profit per hour'],ascending=False))
# print(filterByStation("Nutrition unit level 3",result).sort_values(by=['profit per hour'],ascending=False))
#
# print(filterByStation("Lavatory level 1",result).sort_values(by=['profit per hour'],ascending=False))
# print(filterByStation("Lavatory level 2",result).sort_values(by=['profit per hour'],ascending=False))
# print(filterByStation("Lavatory level 3",result).sort_values(by=['profit per hour'],ascending=False))
#
# print(filterByStation("Medstation level 1",result).sort_values(by=['profit per hour'],ascending=False))
# print(filterByStation("Medstation level 2",result).sort_values(by=['profit per hour'],ascending=False))
# print(filterByStation("Medstation level 3",result).sort_values(by=['profit per hour'],ascending=False))
#
# print(filterByStation("Workbench level 1",result).sort_values(by=['profit per hour'],ascending=False))
# print(filterByStation("Workbench level 2",result).sort_values(by=['profit per hour'],ascending=False))
# print(filterByStation("Workbench level 3",result).sort_values(by=['profit per hour'],ascending=False))
