import discord

def to_millions(value):
    return round(value/1_000_000, 2)

def user_tag_from_author(author) -> str:
    return f"{author.name}#{author.discriminator}"

async def get_user_id(self, ctx, discord_tag):
    (name, disc) = discord_tag.split("#")
    user = discord.utils.get(self.bot.users, name=name, discriminator=disc)
    return user.id

