from config_bot import TOKEN
from discord.ext import commands
import pandas as pd
pd.options.mode.chained_assignment = None

bot = commands.Bot(command_prefix='!')
station_keyword = ['Workbench', 'Medstation', 'Nutrition', 'Lavatory']


# command to clear channel messages
@bot.command(name='clear')
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
    await ctx.send("Messages have been cleared")


# command for showing tarkov crafts.
@bot.command(name='crafts', help=f"args:{','.join(station_keyword)}")
async def give_stats(ctx, arg):
    # sorts the data by profit per hour index
    df = pd.read_csv("Data/TarkovData.csv")
    df = df[df['profit_per_hour'] > 0]
    if arg == 'help':
        await ctx.send(f"use this command with following argument: {','.join(station_keyword)}")
    elif arg in station_keyword:
        if arg == 'Nutrition':
            arg = 'Nutrition unit'
        # prints all data from all 3 of a given station
        new_df = df.loc[df['station'].str.contains(arg)]
        new_df.drop(['station', 'output_price', 'input_price', 'duration', 'profit'], axis=1, inplace=True)
        if not new_df.empty:
            new_df = new_df.sort_values(by=['profit_per_hour'], ascending=False)
            await ctx.send(f"**{arg} - Sorted by profit per hour**")
            await ctx.send(new_df.to_string(index=False))
    elif arg == 'all':
        await ctx.send(f"**Top crafts by profit per hour**")
        # outputs top 10 columns sorted by profit_per_hour
        df.drop(['station', 'output_price', 'input_price', 'duration'], axis=1, inplace=True)
        df = df.iloc[:10, :]
        await ctx.send(df.to_string(index=False))
    else:
        await ctx.send("wrong command argument, use !TarkovStats help to see available arguments")

bot.run(TOKEN)
