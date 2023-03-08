import discord
from discord.ext import commands


class TestCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="ping", description="I love men.")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(content="hello there!", ephemeral=False)


def setup(bot: commands.Bot):
    bot.add_cog(TestCog(bot))
