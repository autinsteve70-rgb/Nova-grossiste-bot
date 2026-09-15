import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CATEGORIE_COMMANDES = "📦 Commande"


@bot.event
async def on_ready():
    print(f"Bot connecté : {bot.user}")


@bot.command()
async def commande(ctx, membre: discord.Member, numero: str, *, details: str):
    """
    Exemple :
    !commande @Jean 001 Batterie x2, Bougie x1
    """

    categorie = discord.utils.get(
        ctx.guild.categories,
        name=CATEGORIE_COMMANDES
    )

    if not categorie:
        await ctx.send("❌ La catégorie 📦 Commande est introuvable.")
        return

    nom_client = membre.display_name.lower().replace(" ", "-")

    salon = await ctx.guild.create_text_channel(
        f"commande-{numero}-{nom_client}",
        category=categorie
    )

    message = (
        f"📦 **NOUVELLE COMMANDE #{numero}**\n\n"
        f"👤 **Client :** {membre.mention}\n"
        f"📋 **Commande :**\n{details}\n\n"
        "⏳ **Statut :** Nouvelle commande"
    )

    await salon.send(message)

    await ctx.send(
        f"✅ Commande **#{numero}** créée dans {salon.mention}."
    )


@bot.command()
async def dm(ctx, membre: discord.Member, *, message: str):
    """
    Exemple :
    !dm @Jean Votre commande est prête !
    """

    try:
        await membre.send(
            f"📦 **NOVA GROSSISTE**\n\n{message}"
        )

        await ctx.send(
            f"✅ Message envoyé en DM à {membre.mention}."
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Impossible d'envoyer un DM à ce membre."
        )


bot.run(TOKEN)
