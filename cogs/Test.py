import discord
from discord.ext import commands


class TestCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="echo", description="repeat after me", aliases="copy")
    async def echo(self, ctx: discord.ApplicationContext, echotext):
        """
        Repeats back to you!
        """
        await ctx.respond(content=f" You said: {echotext}", ephemeral=False)


def setup(bot: commands.Bot):
    bot.add_cog(TestCog(bot))
