#!/usr/bin/env python3
import aiohttp
import bspump
import bspump.common
import bspump.http
import bspump.trigger
import pandas as pd
import bspump.file

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


class IOHTTPSource(bspump.TriggerSource):
    def __init__(self, app, pipeline, choice=None, id=None, config=None):
        super().__init__(app, pipeline, id=id, config=config)

    async def cycle(self):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://tarkov-tools.com/graphql', json={'query': new_query}) as response:
                if response.status == 200:
                    event = await response.json()
                else:
                    raise Exception("Query failed to run by returning code of {}. {}".format(response.status, new_query))
                await self.process(event)


class FilterByStation(bspump.Processor):
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=None, config=None)

    def process(self, context, event):
        my_columns = ['station', 'name', 'output_price', 'duration', 'input_price', 'profit', 'profit_per_hour']
        df = pd.DataFrame(columns=my_columns)
        duration = 0
        for item in event["data"]["crafts"]:
            duration = round((item["duration"])/60/60,ndigits=3)
            reward = item["rewardItems"]
            name_output = reward[0]["item"]["shortName"]
            input_price = 0
            quantity = reward[0]["quantity"]
            output_item = reward[0]["item"]["lastLowPrice"]
            if output_item is None:
                output_item = 0
            output_price = quantity * int(output_item)
            station_name = item["source"]
            profit = 0
            profit_p_hour = 0
            for item2 in range(len(item["requiredItems"])):
                quantity_i = item["requiredItems"][item2]["quantity"]
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
            event = df
        return event


class DataFrameToCSV(bspump.Processor):
    def __init__(self, app, pipeline, id=None, config=None):
        super().__init__(app, pipeline, id=None, config=None)

    def process(self, context, event):
        event.to_csv('./Data/TarkovData.csv', index=False)
        return event


class SamplePipeline(bspump.Pipeline):

    def __init__(self, app, pipeline_id):
        super().__init__(app, pipeline_id)

        self.build(
            IOHTTPSource(app,self).on(bspump.trigger.PeriodicTrigger(app, 20)),
            FilterByStation(app,self),
            bspump.common.PPrintProcessor(app,self),
            DataFrameToCSV(app,self),
            bspump.common.PPrintSink(app, self),
            bspump.common.NullSink(app, self),
        )


if __name__ == '__main__':
    app = bspump.BSPumpApplication()
    svc = app.get_service("bspump.PumpService")
    # Construct and register Pipeline
    pl = SamplePipeline(app, 'SamplePipeline')
    svc.add_pipeline(pl)

    app.run()
