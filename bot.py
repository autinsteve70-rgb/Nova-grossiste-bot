import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot connecté : {bot.user}")


@bot.command()
async def code(ctx, membre: discord.Member, commande: str, code_retrait: str):
    """
    Exemple :
    !code @Jean 001 5837
    """

    try:
        message = (
            "📦 **NOVA GROSSISTE**\n\n"
            "Votre colis est disponible !\n\n"
            f"🧾 **Commande :** #{commande}\n"
            f"🔐 **Code de retrait :** `{code_retrait}`\n\n"
            "📍 Vous pouvez venir récupérer votre colis.\n"
            "Merci — **Nova Grossiste**"
        )

        await membre.send(message)

        await ctx.send(
            f"✅ Le code de retrait a été envoyé en DM à {membre.mention}."
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Impossible d'envoyer un DM à ce membre. "
            "Ses messages privés sont probablement désactivés."
        )


bot.run(TOKEN)
