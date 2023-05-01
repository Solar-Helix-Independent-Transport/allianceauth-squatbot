# Cog Stuff
from collections import defaultdict
import logging
from aadiscordbot.cogs.utils.decorators import is_admin

from allianceauth.eveonline.evelinks import evewho
from allianceauth.eveonline.models import EveAllianceInfo
from allianceauth.services.modules.discord.models import DiscordUser
from discord import SlashCommandGroup, option
from django.utils import timezone
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands
from django.conf import settings
from django.core.cache import cache

from . import app_settings, constants, tasks

logger = logging.getLogger(__name__)


class Squats(commands.Cog):
    ALLIANCE = None

    """
    ITS LEG DAY!!
    """
    squat_commands = SlashCommandGroup("squatbot", "AuthBot Demands Squats!", guild_ids=[
                                       int(settings.DISCORD_GUILD_ID)])
    rep_commands = SlashCommandGroup("repbot", "AuthBot Demands REPS!", guild_ids=[
                                       int(settings.DISCORD_GUILD_ID)])

    @squat_commands.command(name='status', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def sq_slash_stat(
        self,
        ctx,
    ):
        """
            Squats were so last month
        """
        return await ctx.respond("Squats were so last month, try `\repbot status` instead", ephemeral=True)

    @squat_commands.command(name='claim', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def sq_slash_claim(
        self,
        ctx,
    ):
        """
            Squats were so last month
        """
        return await ctx.respond("Squats were so last month, try `\repbot claim` instead", ephemeral=True)

    @rep_commands.command(name='status', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def slash_stat(
        self,
        ctx,
    ):
        """
            Show the current Rep Deficit/Surplus
        """
        c = cache.get(constants.LOSS_KEY, {})
        month_key = timezone.now().strftime(constants.TZ_STRING)
        month = c.get(month_key, {})
        losses = month.get(constants.JSON_LOS_KEY, 0) * 5
        current = cache.get(constants.SQUAT_KEY, {month_key: {}})
        total = 0
        for x in current[month_key].values():
            total += x
        
        gap = "          "
        leaderboard = [f"{t}{gap[len(str(t)):10]}{c}" for c,t in {k: v for k, v in sorted(current[month_key].items(), key=lambda item: item[1], reverse=True)}.items()]
        message = "\n".join(leaderboard[:10])
        extra_message = cache.get(constants.MESSAGE_KEY, "")

        # tasks.sqb_sync_losses.delay()
        e = Embed(title="RepBot!",
                  description=f"`{self.ALLIANCE.alliance_name}` has lost {losses} ships this month, Authbot Demands 5 Reps for each Loss!\n{extra_message}\nUse `/repbot claim` to get swole! :muscle: \nNO CHEATING AuthBot will know!! :eyes:\n\n**Top 10 leaderboard:**\n```\n{message}\n```")

        e.add_field(name="Required Reps", value=f"{losses}")
        if losses - total > 0:
            e.add_field(name="Rep Deficit",
                        value=f"{losses - total}", inline=False)
        else:
            e.add_field(name="Rep Surplus",
                        value=f"{abs(losses - total)}", inline=False)

        return await ctx.respond(embed=e)


    @rep_commands.command(name='claim', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    @option("count", int, min_value=10, max_value=100, description="Number of reps to claim!",)
    async def slash_claim(
        self,
        ctx,
        count
    ):
        month_key = timezone.now().strftime(constants.TZ_STRING)
        main_character = DiscordUser.objects.get(
            uid=ctx.author.id).user.profile.main_character
        current = cache.get(constants.SQUAT_KEY, {month_key: {}})
        if not current.get(month_key, False):
            current[month_key] = {}
        user = current[month_key].get(main_character)
            
        if user == None:
            current[month_key][main_character] = 0
            user = 0

        current[month_key][main_character] = user + count
        setted = cache.set(constants.SQUAT_KEY, current, 60*60*24*90)
        
        month = cache.get(constants.LOSS_KEY, {}).get(month_key, {})
        losses = month.get(constants.JSON_LOS_KEY, 0) * 5
        current = cache.get(constants.SQUAT_KEY, {month_key: {}})
        total = 0
        for x in current.get(month_key,{}).values():
            total += x
        if total > losses:
            return await ctx.respond(f"{main_character} claimed {count} reps! We are now ahead of the losses! HELL YEAH! :muscle:\nKeep it up!")
        return await ctx.respond(f"{main_character} claimed {count} reps! Hell YEAH! :muscle:")


    @rep_commands.command(name='message', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    @option("message", description="What extra message do you want?",)
    async def slash_msg(
        self,
        ctx,
        message
    ):
        if is_admin(ctx.author.id):
            main_character = DiscordUser.objects.get(
                uid=ctx.author.id).user.profile.main_character
            msg = message.replace("\\n", "\n")
            print(msg)
            setted = cache.set(constants.MESSAGE_KEY, msg, 60*60*24*90)
            return await ctx.respond(f"{main_character} set the message to\n {msg}")


    @rep_commands.command(name='sync', guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def slash_sync(
        self,
        ctx,
    ):
        if is_admin(ctx.author.id):
            tasks.sqb_sync_losses.delay()
            return await ctx.respond(f"Syncing Losses", ephemeral=True)


# is_admin
def setup(bot):
    cog = Squats(bot)
    cog.ALLIANCE = EveAllianceInfo.objects.get(
        alliance_id=app_settings.SQUATBOT_ALLIANCE)

    bot.add_cog(cog)
