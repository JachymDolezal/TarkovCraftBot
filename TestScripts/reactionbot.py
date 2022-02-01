import discord

@client.command()
async def embedpages(ctx):
    page1 = discord.Embed(
        title='Page 1/3',
        description='Description',
        colour=discord.Colour.orange()
    )
    page2 = discord.Embed(
        title='Page 2/3',
        description='Description',
        colour=discord.Colour.orange()

    )
    page3 = discord.Embed(
        title='Page 3/3',
        description='Description',
        colour=discord.Colour.orange()
    )

    pages = [page1, page2, page3]

    message = await ctx.send(embed=page1)
    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')

    def check(reaction, user):
        return user == ctx.author

    i = 0
    reaction = None

    while True:
        if str(reaction) == '⏮':
            i = 0
            await message.edit(embed=pages[i])
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed=pages[i])
        elif str(reaction) == '▶':
            if i < 2:
                i += 1
                await message.edit(embed=pages[i])
        elif str(reaction) == '⏭':
            i = 2
            await message.edit(embed=pages[i])

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()