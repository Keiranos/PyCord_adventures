import discord
from discord.ext import commands
from config import RED, PREFIX, MAIN
from utils.utils import chunks, Page
import datetime as dt
import re

mention = re.compile(r"<@!?[0-9]{15,20}>")


async def help_embed(ctx: commands.Context, bot: commands.Bot, command: commands.Command):
    p = ctx.prefix if not mention.match(ctx.prefix) else PREFIX
    em = discord.Embed(colour=MAIN)
    em.set_thumbnail(url=bot.user.display_avatar.url)

    args = command.clean_params  # get the arguments the command takes
    args = " ".join([f"<{x.name.replace('_', ' ')}>" for x in [args[i] for i in args]])  # Join the args together
    # qualified_name is the full command name in the case of a child command
    command_names = [x for x in [command.name] + command.aliases if not x.startswith("_")]
    name = command_names.pop(0)  # get 1st name
    parent = command.full_parent_name + " " if command.full_parent_name else ""
    em.description = f"**{p}{parent}{name} {args}**\n"  # create first line

    if command_names:  # add aliases if they exist
        aliases = ", ".join(sorted(command_names))
        em.description += f"**Aliases:** {aliases}\n"
    if command.help:
        em.description += command.help
    else:
        em.description += "*No help text is set*"

    if isinstance(command, commands.Group):  # if is a command group (has child commands)
        em.description += "\n\n**Child commands:**\n"
        child = []
        for x in command.commands:
            try:  # Only add command if the user is allowed to run it
                can_run = await x.can_run(ctx)
            except commands.CommandError:
                can_run = False
            if can_run:  # can_run can raise an error or return false, so use a bool to check
                name = next((x for x in [x.name] + x.aliases if not x.startswith("_")), x.name)
                parent = x.full_parent_name + " " if x.full_parent_name else ""
                child.append(f"▫ {p}{parent}{name}")  # append commands
        em.description += "\n".join(sorted(child))

    em.set_footer(icon_url=ctx.guild.icon.url, text=ctx.guild.name)
    em.timestamp = dt.datetime.utcnow()
    return em


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(aliases="pingcheck")
    async def ping(self, ctx: discord.ApplicationContext):
        """
        Displays the ping of discord
        """
        msg = f"Pong!\nDiscord latency: {self.bot.latency * 1000:.0f}ms"
        await ctx.respond(content=msg, ephemeral=False)

    @commands.command(aliases=["commands"], hidden=True)
    async def help(self, ctx: commands.Context, *, command=""):
        """
        You are here
        Shows information on a given command. If no command is provided, all available commands will be listed
        `command` can also be a page number or the title of a certain page in order to jump to the given page
        """
        p = ctx.prefix if not mention.match(ctx.prefix) else PREFIX  # command prefix
        if not command or not self.bot.get_command(command):  # if no argument provided or not a command

            emb_template = discord.Embed(colour=MAIN, title="Command List", description="")
            emb_template.set_thumbnail(url=self.bot.user.display_avatar.url)
            emb_template.set_footer(text=f"Use '{p}help [command]' for more information on a command",
                                    icon_url=ctx.guild.icon.url)
            emb_template.timestamp = dt.datetime.utcnow()
            pages = []

            cogs = self.bot.cogs.values()
            for cog in sorted(cogs, key=lambda x: x.qualified_name):  # look through cogs
                embed = emb_template.copy()  # create base embed
                embed.description = f"**{cog.qualified_name}**"

                # iterate through commands
                cog_commands = sorted([x for x in cog.walk_commands()], key=lambda x: x.qualified_name.replace("_", ""))
                cog_commands = [x for x in cog_commands if isinstance(x, commands.Command)]  # Don't include slash cmds
                for cmd in cog_commands:
                    # Check if command can be run by user
                    try:
                        can_run = await cmd.can_run(ctx)
                    except commands.CommandError:
                        can_run = False
                    if cmd.enabled and can_run and not  cmd.hidden:  # if command can be run by user and isnt hidden
                        # add a description based on the command docstring
                        if isinstance(cmd, commands.Group):  # if is a command group
                            continue  # ignore command groups, skip to next iteration
                        elif cmd.short_doc:  # if a help command is set
                            desc = cmd.short_doc  # First line of docstring
                        else:
                            desc = "*No help text is set*"
                        # Get first alias that doesn't have an _ at the front
                        name = next((x for x in [cmd.name] + cmd.aliases if not x.startswith("_")), cmd.name)
                        parent = cmd.full_parent_name + " " if cmd.full_parent_name else ""
                        embed.add_field(name=f"{p}{parent}{name}", value=desc, inline=False)
                if embed.fields:  # if no commands, don't add page
                    if len(embed.fields) > 10:  # if more than 10 commands
                        fields = chunks(embed.fields, 10)  # chunk the fields
                        for cmd, chunk in enumerate(fields):  # for every chunk
                            embed = emb_template.copy()  # new embed
                            embed.description = f"**{cog.qualified_name}:** {cmd + 1}"
                            for field in chunk:
                                embed.add_field(name=field.name, value=field.value, inline=False)  # populate
                            pages.append(embed)
                    else:
                        pages.append(embed)

            if command:  # if a page # or cog name is specified, jump to that
                if command.isdigit():  # if a number
                    command = int(command) - 1  # get page index
                    # Constrain from 0 to N
                    if command < 0:
                        command = 0
                    elif command >= len(pages):
                        command = len(pages) - 1
                    page = pages[command]  # get the requested page
                else:  # A string was given
                    page = None
                    for cmd in pages:
                        if command.lower() in cmd.description.lower():  # if the page matches the cog name
                            page = cmd
                            break
                    if not page:
                        em = discord.Embed(colour=RED, title=f"⛔ Error: Page/Command Not Found")
                        em.set_footer(icon_url=ctx.guild.icon.url, text=ctx.guild.name)
                        em.timestamp = dt.datetime.utcnow()
                        return await ctx.send(embed=em)
            else:  # No page specified, default to 1st page
                page = pages[0]

            # Create message and start pagination
            view = Page(ctx, pages, footer=pages[0].footer.text, index=pages.index(page))
            page = view.set_embed_footer(page)
            await ctx.send(embed=page, view=view)

        else:  # if a command is passed
            command = self.bot.get_command(command)
            if not command:
                return await ctx.send("🔍 I cannot find that command/page")

            # verify command can be run by the user
            try:
                can_run = await command.can_run(ctx)
            except commands.CommandError:
                can_run = False
            if not command.enabled or not can_run:
                em = discord.Embed(colour=RED, title=f"⛔ Error: That Command Isn't Available to You")
                em.set_footer(icon_url=ctx.guild.icon.url, text=ctx.guild.name)
                em.timestamp = dt.datetime.utcnow()
                return await ctx.send(embed=em)

            em = await help_embed(ctx, self.bot, command)  # send help embed for that command
            await ctx.send(embed=em)
def setup(bot: commands.Bot):
    bot.add_cog(Misc(bot))
