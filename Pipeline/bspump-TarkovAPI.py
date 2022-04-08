#!/usr/bin/env python3
import aiohttp
import bspump
import bspump.common
import bspump.http
import bspump.trigger
import pandas as pd
import bspump.file

query = """
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


class IOHTTPSource(bspump.TriggerSource):
    def __init__(self, app, pipeline, choice=None, id=None, config=None):
        super().__init__(app, pipeline, id=id, config=config)

    async def cycle(self):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://tarkov-tools.com/graphql', json={'query': query}) as response:
                if response.status == 200:
                    event = await response.json()
                else:
                    raise Exception("Query failed to run by returning code of {}. {}".format(response.status, query))
                await self.process(event)


class FilterByStation(bspump.Processor):
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=None, config=None)

    def process(self, context, event):
        my_columns = ['station', 'name', 'output_price_item', 'duration', 'input_price_item', 'profit', 'profit_per_hour']
        df = pd.DataFrame(columns=my_columns)
        for item in event["data"]["crafts"]:
            duration = round((item["duration"])/60/60, ndigits=3)
            reward = item["rewardItems"][0]
            name_output = reward["item"]["shortName"]
            quantity = reward["quantity"]
            output_item_price = reward["item"]["lastLowPrice"]
            if output_item_price is None:  # checks for NULL values
                output_item_price = 0
            output_price_item = quantity * int(output_item_price)
            station_name = item["source"]
            profit = 0
            profit_p_hour = 0
            input_price_item = 0
            for item2 in range(len(item["requiredItems"])):
                required_item = item["requiredItems"][item2]
                quantity_i = required_item["quantity"]
                input_item = required_item["item"]["lastLowPrice"]
                if input_item is None:
                    input_item = 0
                price_of_input_item = input_item * quantity_i
                input_price_item = input_price_item + price_of_input_item
                profit = output_price_item - input_price_item
                profit_p_hour = round(profit / duration, ndigits=3)
            df = df.append(
                pd.Series([station_name,
                           name_output,
                           output_price_item,
                           duration,
                           input_price_item,
                           profit,
                           profit_p_hour],
                          index=my_columns), ignore_index=True)
            event = df
        return event


class DataFrameToCSV(bspump.Processor):
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=None, config=None)

    def process(self, context, event):
        event.to_csv('./Discordbot/Data/TarkovData.csv', index=False)
        return event


class SamplePipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)

        self.build(
            IOHTTPSource(app, self).on(bspump.trigger.PeriodicTrigger(app, 5)),
            FilterByStation(app, self),
            bspump.common.PPrintProcessor(app, self),
            DataFrameToCSV(app, self),
            bspump.common.NullSink(app, self),
        )


if __name__ == '__main__':
    app = bspump.BSPumpApplication()
    svc = app.get_service("bspump.PumpService")
    pl = SamplePipeline(app, 'SamplePipeline')
    svc.add_pipeline(pl)

    app.run()
