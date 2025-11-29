import os
import asyncio
import signal
import discord
from discord.ext import commands
from dotenv import load_dotenv

from structures.linked_list import LinkedListHistory
from structures.tree import sample_tree, TreeNode
from structures.persistence import save_data, load_data

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# --- Structures en mémoire ---
history = LinkedListHistory()
conversation_tree: TreeNode = sample_tree()
user_states: dict[int, str] = {}  # user_id -> node_key
warnings: dict[int, int] = {}     # avertissements langage
guess_games: dict[int, int] = {}  # mini-jeu

# --- Persistence ---
def dump_all_data() -> dict:
    return {
        "history": history.to_list(),   # utilise to_list (liste de dicts)
        "tree": conversation_tree.to_dict(),
        "user_states": {str(k): v for k, v in user_states.items()},
        "warnings": {str(k): v for k, v in warnings.items()},
        "guess_games": {str(k): v for k, v in guess_games.items()}
    }

def load_all_data():
    global history, conversation_tree, user_states, warnings, guess_games
    data = load_data()
    if not data:
        return
    history.from_list(data.get("history", []))   # utilise from_list
    if "tree" in data:
        conversation_tree = TreeNode.from_dict(data["tree"])
    user_states = {int(k): v for k, v in data.get("user_states", {}).items()}
    warnings = {int(k): v for k, v in data.get("warnings", {}).items()}
    guess_games = {int(k): v for k, v in data.get("guess_games", {}).items()}

load_all_data()

# --- Historique ---
@bot.command(name="h_last")
async def h_last(ctx):
    last = history.get_last_for_user(ctx.author.id)
    await ctx.send(f"Dernière commande : `{last}`" if last else "Aucune commande.")

@bot.command(name="h_all")
async def h_all(ctx):
    allc = history.get_all_for_user(ctx.author.id)
    if allc:
        pretty = "\n".join(f"- {c}" for c in allc)
        await ctx.send(f"Historique complet :\n{pretty}")
    else:
        await ctx.send("Historique vide.")

@bot.command(name="h_clear")
async def h_clear(ctx):
    history.clear_for_user(ctx.author.id)
    await ctx.send("Ton historique a été vidé.")

# --- Conversation / arbre ---
@bot.command(name="helpme")
async def start_conversation(ctx):
    user_states[ctx.author.id] = conversation_tree.key
    await ctx.send(conversation_tree.prompt)

@bot.command(name="reset")
async def reset_convo(ctx):
    user_states[ctx.author.id] = conversation_tree.key
    await ctx.send("Discussion réinitialisée. " + conversation_tree.prompt)

@bot.command(name="speak_about")
async def speak_about(ctx, *, topic: str):
    exists = conversation_tree.find_topic(topic)
    await ctx.send("oui" if exists else "non")

# --- Filtre langage (supplémentaire) ---
BAD_WORDS = {"con", "idiot", "merde"}

def contains_bad_word(text: str) -> bool:
    words = [w.strip(".,!?;:()[]{}\"'").lower() for w in text.split()]
    return any(w in BAD_WORDS for w in words)

@bot.command(name="warnings")
async def show_warnings(ctx, member: discord.Member = None):
    target = member or ctx.author
    count = warnings.get(target.id, 0)
    await ctx.send(f"Avertissements pour {target.mention} : {count}")

# --- Rappels (supplémentaire) ---
def parse_duration(text: str) -> int | None:
    text = text.lower().strip()
    try:
        if text.endswith("s"):
            return int(text[:-1])
        if text.endswith("m"):
            return int(text[:-1]) * 60
        if text.endswith("h"):
            return int(text[:-1]) * 3600
    except ValueError:
        return None
    return None

@bot.command(name="remind")
async def remind(ctx, duration: str, *, message_text: str):
    seconds = parse_duration(duration)
    if not seconds or seconds <= 0:
        await ctx.send("Durée invalide. Ex: 30s, 10m, 1h.")
        return
    await ctx.send(f"Rappel dans {duration}.")
    async def task():
        await asyncio.sleep(seconds)
        await ctx.send(f"{ctx.author.mention} Rappel: {message_text}")
    asyncio.create_task(task())

# --- Mini-jeu Guess (supplémentaire) ---
@bot.command(name="guess")
async def guess(ctx, action: str, number: int = None):
    uid = ctx.author.id
    action = action.lower().strip()
    if action == "start":
        import random
        guess_games[uid] = random.randint(1, 10)
        await ctx.send("J’ai choisi un nombre entre 1 et 10. Devine avec `!guess try X`.")
    elif action == "stop":
        guess_games.pop(uid, None)
        await ctx.send("Partie arrêtée.")
    elif action == "try":
        target = guess_games.get(uid)
        if target is None:
            await ctx.send("Pas de partie en cours. Lance avec `!guess start`.")
            return
        if number is None:
            await ctx.send("Utilise `!guess try 5` (donne un nombre).")
            return
        if number < 1 or number > 10:
            await ctx.send("Le nombre doit être entre 1 et 10.")
            return
        if number == target:
            await ctx.send("Bravo, gagné !")
            guess_games.pop(uid, None)
        elif number < target:
            await ctx.send("Trop petit.")
        else:
            await ctx.send("Trop grand.")
    else:
        await ctx.send("Actions valides: start / try X / stop")

# --- Gestion messages ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Historique (enregistrer toutes les interactions, commandes incluses)
    history.push(message.author.id, message.content)

    # Filtre langage
    if contains_bad_word(message.content):
        warnings[message.author.id] = warnings.get(message.author.id, 0) + 1
        await message.channel.send(f"Attention {message.author.mention}, langage inapproprié. Avertissements: {warnings[message.author.id]}")

    # Conversation: si en cours, traiter réponse sans préfixe
    if message.author.id in user_states and not message.content.startswith(PREFIX):
        def find_node(node: TreeNode, key: str) -> TreeNode | None:
            if node.key == key:
                return node
            for c in node.children:
                found = find_node(c, key)
                if found:
                    return found
            return None

        current = find_node(conversation_tree, user_states[message.author.id])
        if current:
            answer = message.content.strip().lower()
            matched = next((c for c in current.children if c.key.lower() == answer), None)
            if matched:
                user_states[message.author.id] = matched.key
                if matched.conclusion:
                    await message.channel.send(f"Conclusion : {matched.conclusion}")
                    user_states.pop(message.author.id, None)
                else:
                    await message.channel.send(matched.prompt)
            else:
                options = ", ".join(c.key for c in current.children)
                await message.channel.send(f"Options valides : {options}")

    await bot.process_commands(message)

# --- Sauvegarde ---
async def safe_shutdown():
    save_data(dump_all_data())
    await bot.close()

def handle_signal(sig):
    try:
        asyncio.get_event_loop().create_task(safe_shutdown())
    except RuntimeError:
        save_data(dump_all_data())

try:
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: handle_signal("SIGINT"))
    loop.add_signal_handler(signal.SIGTERM, lambda: handle_signal("SIGTERM"))
except NotImplementedError:
    pass

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user} (id: {bot.user.id})")

if __name__ == "__main__":
    async def autosave():
        while True:
            await asyncio.sleep(60)
            save_data(dump_all_data())
    loop = asyncio.get_event_loop()
    loop.create_task(autosave())
    try:
        bot.run(TOKEN)
    finally:
        save_data(dump_all_data())
