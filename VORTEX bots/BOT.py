# import libraries
import os
import discord
from discord.ext import commands
from discord import Intents
import random
import requests
import json
import pickle
from dotenv import load_dotenv
from discord.utils import get
import asyncio
from discord.ext import tasks
import time  # time for mining cooldowns
import tweepy
from datetime import datetime, timedelta



# Load environment variables
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
SOL_API_KEY


# Create Intents object
intents = Intents.default()
intents.members = True
intents.message_content = True

# Create bot with intents
bot = commands.Bot(command_prefix='!', intents=intents, help_command=commands.DefaultHelpCommand())

# Data storage
polls = {}
vortex_coins = {}
user_balances = {}
user_addresses = {}
coins = {}


# Events
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Connected to {len(bot.guilds)} guilds')
    print(f'Bot latency: {round(bot.latency * 1000)}ms')
    auto_save.start()

# ... (include all the existing commands from dapp.py, cryptomining.py, quiz.py, and game.py)
# create a class or a way to get the commands working


class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='greet')
    async def greet(self, ctx):
        await ctx.send('Hello!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if 'hello' in message.content.lower():
            await message.channel.send('Hi there!')

# To add the cog to the bot
bot.add_cog(MyCog(bot))

# Helper functions
def save_questions(questions, filename="questions.pkl"):
    with open(filename, 'wb') as file:
        pickle.dump(questions, file)

async def send_message(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)
    else:
        print(f"Channel with ID {channel_id} not found.")

async def handle_error(ctx, error):
    await ctx.send(f'An error occurred: {str(error)}')

def reward_coins(guild_id, user_id, coins_to_reward):
    if guild_id in vortex_coins:
        vortex_coins[guild_id][user_id] = vortex_coins[guild_id].get(user_id, 0) + coins_to_reward
    else:
        vortex_coins[guild_id] = {user_id: coins_to_reward}

class DappCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def create_poll(self, ctx, question: str, *options: str):
        if len(options) < 2:
            await ctx.send("A poll requires at least two options.")
            return
        if len(options) > 10:
            await ctx.send("A poll can have a maximum of 10 options.")
            return

        poll_id = len(polls) + 1
        polls[poll_id] = {'question': question, 'options': options, 'votes': {}}

        embed = discord.Embed(title="Poll",
                            description=question,
                            color=discord.Color.blue())
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        for i, option in enumerate(options):
            embed.add_field(name=f"Option {i + 1}", value=option, inline=False)

        poll_message = await ctx.send(embed=embed)
        for i in range(len(options)):
            await poll_message.add_reaction(reactions[i])

    @commands.command()
    async def vote(self, ctx, poll_id: int, option_index: int):
        user = ctx.author
        if poll_id in polls:
            poll = polls[poll_id]
            if 0 <= option_index < len(poll['options']):
                poll['votes'][user.id] = option_index
                await ctx.send(f"{user.display_name} voted in poll {poll_id}.")
            else:
                await ctx.send("Invalid option index.")
        else:
            await ctx.send("Poll not found.")

    @commands.command()
    async def end_poll(self, ctx, poll_id: int):
        if poll_id in polls:
            poll = polls[poll_id]
            results = [0] * len(poll['options'])
            for vote in poll['votes'].values():
                results[vote] += 1
            result_message = "Poll Results:\n"
            for i, option in enumerate(poll['options']):
                result_message += f"Option {i + 1} ({option}): {results[i]} votes\n"
            await ctx.send(result_message)
            del polls[poll_id]
        else:
            await ctx.send("Poll not found.")

    @commands.command()
    @commands.has_role('Admin')
    async def add_premium(self, ctx, member: discord.Member):
        role = get(ctx.guild.roles, name="Premium")
        if not role:
            role = await ctx.guild.create_role(name="Premium", color=discord.Color.gold())
        await member.add_roles(role)
        await ctx.send(f"{member.display_name} has been given Premium membership.")

    @commands.command()
    @commands.has_role('Admin')
    async def remove_premium(self, ctx, member: discord.Member):
        role = get(ctx.guild.roles, name="Premium")
        if role:
            await member.remove_roles(role)
            await ctx.send(f"Premium membership removed from {member.display_name}.")
        else:
            await ctx.send("Premium role not found.")

    @commands.command()
    async def functionalities(self, ctx):
        print(f"Functionalities command triggered by {ctx.author}")  # Debug line
        functions = """
        **Available Commands:**
        
        **Quiz Commands:**
        • !quiz <category> - Start a quiz
        • !answer <your_answer> - Answer the current quiz
        • !hint - Get a hint for the current quiz
        
        **Economy Commands:**
        • !balance - Check your VortexCoin balance
        • !daily - Get daily reward
        • !transfer <@user> <amount> - Transfer VortexCoins
        • !leaderboard - View top 10 richest users
        
        **Mining Commands:**
        • !start_mining [rig_type] - Start mining (basic/medium/advanced)
        • !mining_stats - View mining rig statistics
        • !upgrade_rig - Check rig upgrade information
        
        **Poll Commands:**
        • !create_poll <question> <options> - Create a poll
        • !vote <poll_id> <option_index> - Vote in a poll
        • !end_poll <poll_id> - End a poll
        
        **Crypto Commands:**
        • !register_wallet <address> - Register your crypto wallet
        • !crypto_price <symbol> - Check crypto prices
        
        **DAO Governance Commands:**
        • !create_proposal <title> <duration_hours> <description> - Create a governance proposal
        • !vote <proposal_id> <yes/no/abstain> - Vote on a proposal
        • !proposal_status <proposal_id> - Check proposal status
        • !list_proposals [active/completed/all] - List proposals
        • !my_voting_power - Check your voting power
        • !dao_help - Get help with DAO commands
        
        **Admin Commands:**
        • !add_premium <@user> - Grant premium membership
        • !remove_premium <@user> - Revoke premium membership
        • !dao_settings - View DAO settings (Admin only)
        """
        embed = discord.Embed(title="Bot Functionalities", description=functions, color=discord.Color.blue())
        await ctx.send(embed=embed)

# Add this before bot.run()
bot.add_cog(DappCog(bot))

class CryptoMining(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mining_rates = {
            "basic": {"rate": 1, "cost": 0},
            "medium": {"rate": 2, "cost": 1000},
            "advanced": {"rate": 5, "cost": 5000}
        }
        self.active_miners = {}  # Store active mining sessions
        self.mining_cooldowns = {}  # Store mining cooldowns

    @commands.command(name='start_mining')
    async def start_mining(self, ctx, rig_type="basic"):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        # Check cooldown
        if user_id in self.mining_cooldowns:
            if time.time() - self.mining_cooldowns[user_id] < 3600:  # 1-hour cooldown
                remaining = 3600 - (time.time() - self.mining_cooldowns[user_id])
                await ctx.send(f"Mining cooldown active. Try again in {remaining:.0f} seconds.")
                return

        # Validate rig type
        if rig_type not in self.mining_rates:
            await ctx.send(f"Invalid rig type. Choose from: {', '.join(self.mining_rates.keys())}")
            return

        # Check if user can afford the rig
        user_balance = vortex_coins.get(guild_id, {}).get(user_id, 0)
        rig_cost = self.mining_rates[rig_type]["cost"]
        
        if user_balance < rig_cost:
            await ctx.send(f"You need {rig_cost} VortexCoins to use the {rig_type} mining rig!")
            return

        # Deduct rig cost if not basic
        if rig_cost > 0:
            vortex_coins[guild_id][user_id] -= rig_cost

        # Start mining session
        mining_rate = self.mining_rates[rig_type]["rate"]
        mining_duration = random.randint(30, 60)  # Random duration between 30-60 seconds
        reward = mining_rate * mining_duration

        await ctx.send(f"Started mining with {rig_type} rig! Mining for {mining_duration} seconds...")
        await asyncio.sleep(mining_duration)

        # Award coins
        reward_coins(guild_id, user_id, reward)
        self.mining_cooldowns[user_id] = time.time()
        
        await ctx.send(f"Mining complete! You earned {reward} VortexCoins!")

    @commands.command(name='mining_stats')
    async def mining_stats(self, ctx):
        embed = discord.Embed(title="Mining Statistics", color=discord.Color.gold())
        
        for rig, data in self.mining_rates.items():
            embed.add_field(
                name=f"{rig.capitalize()} Rig",
                value=f"Rate: {data['rate']} coins/sec\nCost: {data['cost']} VortexCoins",
                inline=False
            )
            
        await ctx.send(embed=embed)

    @commands.command(name='upgrade_rig')
    async def upgrade_rig(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        user_balance = vortex_coins.get(guild_id, {}).get(user_id, 0)
        
        # Find current rig level
        current_rig = "basic"
        for rig in ["advanced", "medium", "basic"]:
            if user_balance >= self.mining_rates[rig]["cost"]:
                current_rig = rig
                break

        # Calculate next rig
        if current_rig == "basic":
            next_rig = "medium"
        elif current_rig == "medium":
            next_rig = "advanced"
        else:
            await ctx.send("You already have the best mining rig!")
            return

        upgrade_cost = self.mining_rates[next_rig]["cost"]
        await ctx.send(f"Your current rig: {current_rig}\nNext upgrade: {next_rig}\nCost: {upgrade_cost} VortexCoins")

    @commands.command(name='mining_help')
    async def mining_help(self, ctx):
        help_text = """
        **Mining Commands:**
        `!start_mining [rig_type]` - Start mining (basic/medium/advanced)
        `!mining_stats` - View mining rig statistics
        `!upgrade_rig` - Check rig upgrade information
        
        **Mining Rigs:**
        - Basic: Free, 1 coin/sec
        - Medium: 1000 VortexCoins, 2 coins/sec
        - Advanced: 5000 VortexCoins, 5 coins/sec
        
        Note: Mining has a 1-hour cooldown period.
        """
        await ctx.send(help_text)

# Add this before bot.run()
bot.add_cog(CryptoMining(bot))

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='balance')
    async def balance(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        balance = vortex_coins.get(guild_id, {}).get(user_id, 0)
        await ctx.send(f'Your balance: {balance} VortexCoins')

    @commands.command(name='daily')
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        reward = 100
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        reward_coins(guild_id, user_id, reward)
        await ctx.send(f'You claimed your daily reward of {reward} VortexCoins!')

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_quizzes = {}
        self.scores = {}

    @commands.command(name='quiz')
    async def start_quiz(self, ctx, category=None):
        if category not in questions_pool:
            categories = ', '.join(questions_pool.keys())
            await ctx.send(f'Please specify a valid category: {categories}')
            return
        
        question_data = random.choice(questions_pool[category])
        await ctx.send(f"Question: {question_data['question']}\nUse !answer <your_answer> to respond")
        self.active_quizzes[ctx.channel.id] = {
            'data': question_data,
            'user': ctx.author.id,
            'attempts': 0
        }

    @commands.command(name='hint')
    async def hint(self, ctx):
        if ctx.channel.id in self.active_quizzes:
            quiz = self.active_quizzes[ctx.channel.id]
            if quiz['user'] == ctx.author.id:
                await ctx.send(f"Hint: {quiz['data']['hint']}")
            else:
                await ctx.send("This isn't your quiz!")
        else:
            await ctx.send("No active quiz in this channel!")

    @commands.command(name='answer')
    async def answer(self, ctx, *, answer: str):
        if ctx.channel.id in self.active_quizzes:
            quiz = self.active_quizzes[ctx.channel.id]
            
            if quiz['user'] != ctx.author.id:
                await ctx.send("This isn't your quiz!")
                return

            quiz['attempts'] += 1
            correct_answer = quiz['data']['answer'].lower()
            user_answer = answer.lower()

            if user_answer == correct_answer:
                # Calculate reward based on attempts
                reward = max(20 - (quiz['attempts'] - 1) * 5, 5)
                reward_coins(str(ctx.guild.id), str(ctx.author.id), reward)
                await ctx.send(f"Correct! You earned {reward} VortexCoins!")
                del self.active_quizzes[ctx.channel.id]
            else:
                if quiz['attempts'] >= 3:
                    await ctx.send(f"Sorry, you've run out of attempts. The correct answer was: {correct_answer}")
                    del self.active_quizzes[ctx.channel.id]
                else:
                    await ctx.send(f"Wrong answer! You have {3 - quiz['attempts']} attempts remaining. Try using !hint")

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='register_wallet')
    async def register_wallet(self, ctx, wallet_address: str):
        user_id = str(ctx.author.id)
        user_addresses[user_id] = wallet_address
        await ctx.send(f'Wallet address registered successfully!')

    @commands.command(name='crypto_price')
    async def crypto_price(self, ctx, symbol: str):
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
            response = requests.get(url)
            data = response.json()
            price = data[symbol.lower()]['usd']
            await ctx.send(f'{symbol.upper()} price: ${price:,.2f} USD')
        except:
            await ctx.send('Error fetching price. Make sure you used the correct coin ID.')

# Add this before bot.run()
bot.add_cog(Economy(bot))
bot.add_cog(Quiz(bot))
bot.add_cog(Crypto(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is on cooldown. Try again in {error.retry_after:.2f} seconds.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permission to use this command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument! Check !functionalities for command usage.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Invalid argument provided! Check !functionalities for command usage.')
    else:
        await handle_error(ctx, error)

# Load data on startup
def load_data():
    try:
        with open('vortex_data.pkl', 'rb') as f:
            data = pickle.load(f)
            global vortex_coins, user_addresses, polls
            vortex_coins = data.get('vortex_coins', {})
            user_addresses = data.get('user_addresses', {})
            polls = data.get('polls', {})
            
            # Load governance proposals if available
            governance_cog = bot.get_cog('GovernanceDAO')
            if governance_cog and 'governance_proposals' in data:
                governance_cog.proposals = data['governance_proposals']
    except FileNotFoundError:
        print("No existing data file found. Starting fresh.")

# Save data periodically
def save_data():
    with open('vortex_data.pkl', 'wb') as f:
        pickle.dump({
            'vortex_coins': vortex_coins,
            'user_addresses': user_addresses,
            'polls': polls,
            'governance_proposals': getattr(bot.get_cog('GovernanceDAO'), 'proposals', {})
        }, f)

# You might want to call save_data periodically using Discord's tasks instead
@tasks.loop(minutes=10)
async def auto_save():
    save_data()

# Start the auto-save when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Connected to {len(bot.guilds)} guilds')
    print(f'Bot latency: {round(bot.latency * 1000)}ms')
    auto_save.start()

async def setup():
    await bot.add_cog(DappCog(bot))
    await bot.add_cog(CryptoMining(bot))
    await bot.add_cog(Economy(bot))
    await bot.add_cog(Quiz(bot))
    await bot.add_cog(Crypto(bot))
    await bot.add_cog(GovernanceDAO(bot))

# Load data and start bot
load_data()
asyncio.run(setup())
bot.run(DISCORD_BOT_TOKEN)

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = {}
        
    @commands.command(name='level')
    async def check_level(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.levels:
            self.levels[user_id] = {"xp": 0, "level": 1}
        
        level_data = self.levels[user_id]
        embed = discord.Embed(title=f"{ctx.author.name}'s Level", color=discord.Color.blue())
        embed.add_field(name="Level", value=level_data["level"])
        embed.add_field(name="XP", value=f"{level_data['xp']}/100")
        await ctx.send(embed=embed)

    async def add_xp(self, user_id, xp_amount):
        if user_id not in self.levels:
            self.levels[user_id] = {"xp": 0, "level": 1}
            
        self.levels[user_id]["xp"] += xp_amount
        if self.levels[user_id]["xp"] >= 100:
            self.levels[user_id]["level"] += 1
            self.levels[user_id]["xp"] = 0
            return True
        return False

class EnhancedMining(CryptoMining):
    def __init__(self, bot):
        super().__init__(bot)
        self.mining_bonuses = {}
        
    @commands.command(name='mining_bonus')
    async def activate_bonus(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.mining_bonuses:
            self.mining_bonuses[user_id] = 1.5  # 50% bonus
            await ctx.send("🎉 Mining bonus activated! +50% rewards for 1 hour!")
            await asyncio.sleep(3600)  # 1 hour
            del self.mining_bonuses[user_id]
        else:
            await ctx.send("You already have an active mining bonus!")

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='coinflip')
    async def coinflip(self, ctx, bet: int, choice: str):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        if bet <= 0:
            await ctx.send("Bet must be positive!")
            return
            
        if vortex_coins[guild_id][user_id] < bet:
            await ctx.send("Insufficient funds!")
            return
            
        result = random.choice(['heads', 'tails'])
        if choice.lower() == result:
            reward_coins(guild_id, user_id, bet * 2)
            await ctx.send(f"🎉 You won! The coin landed on {result}!")
        else:
            vortex_coins[guild_id][user_id] -= bet
            await ctx.send(f"Sorry, you lost! The coin landed on {result}.")

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.items = {
            "mining_boost": {"price": 500, "description": "2x mining rewards for 1 hour"},
            "premium_badge": {"price": 5000, "description": "Exclusive premium badge"},
            "lottery_ticket": {"price": 100, "description": "Chance to win big!"}
        }

    @commands.command(name='shop')
    async def show_shop(self, ctx):
        embed = discord.Embed(title="VortexCoin Shop", color=discord.Color.green())
        for item, data in self.items.items():
            embed.add_field(
                name=f"{item.replace('_', ' ').title()} - {data['price']} coins",
                value=data['description'],
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name='buy')
    async def buy_item(self, ctx, item: str):
        if item not in self.items:
            await ctx.send("Invalid item!")
            return
            
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        price = self.items[item]["price"]
        
        if vortex_coins[guild_id][user_id] < price:
            await ctx.send("Insufficient funds!")
            return
            
        vortex_coins[guild_id][user_id] -= price
        await ctx.send(f"Successfully purchased {item}!")

class Challenges(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_challenges = {}
        self.generate_challenges.start()

    @tasks.loop(hours=24)
    async def generate_challenges(self):
        self.daily_challenges = {
            "mine_coins": {"goal": 1000, "reward": 500, "description": "Mine 1000 vortexcoins"},
            "win_games": {"goal": 5, "reward": 300, "description": "Win 5 games"},
            "answer_quiz": {"goal": 3, "reward": 200, "description": "Answer 3 quiz questions"}
        }

    @commands.command(name='challenges')
    async def show_challenges(self, ctx):
        embed = discord.Embed(title="Daily Challenges", color=discord.Color.purple())
        for challenge, data in self.daily_challenges.items():
            embed.add_field(
                name=challenge.replace('_', ' ').title(),
                value=f"{data['description']} - Reward: {data['reward']} vortexcoins",
                inline=False
            )
        await ctx.send(embed=embed)

bot.add_cog(LevelSystem(bot))
bot.add_cog(EnhancedMining(bot))
bot.add_cog(Games(bot))
bot.add_cog(Shop(bot))
bot.add_cog(Challenges(bot))

class TwitterRaiding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_raids = {}
        self.raid_cooldowns = {}
        self.raid_participants = {}
        
        # Twitter API credentials (Add these to your .env file)
        auth = tweepy.OAuthHandler(os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_API_SECRET'))
        auth.set_access_token(os.getenv('TWITTER_ACCESS_TOKEN'), os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
        self.twitter_api = tweepy.API(auth)

    @commands.command(name='start_raid')
    @commands.has_role('Raid Manager')
    async def start_raid(self, ctx, tweet_url: str, duration: int = 30, reward: int = 100):
        """
        Start a new Twitter raid
        Usage: !start_raid <tweet_url> [duration_in_minutes] [reward_per_action]
        """
        try:
            # Extract tweet ID from URL
            tweet_id = tweet_url.split('/')[-1]
            tweet = self.twitter_api.get_status(tweet_id)
            
            raid_id = str(ctx.message.id)
            self.active_raids[raid_id] = {
                'tweet_id': tweet_id,
                'tweet_url': tweet_url,
                'start_time': datetime.now(),
                'duration': duration,
                'reward': reward,
                'participants': set(),
                'initial_metrics': {
                    'likes': tweet.favorite_count,
                    'retweets': tweet.retweet_count,
                    'replies': 0  # Base count for replies
                }
            }

            raid_embed = discord.Embed(
                title="🚀 Twitter Raid Started!",
                description=f"Let's raid this tweet!\n{tweet_url}",
                color=discord.Color.blue()
            )
            raid_embed.add_field(name="Duration", value=f"{duration} minutes")
            raid_embed.add_field(name="Reward per Action", value=f"{reward} VortexCoins")
            raid_embed.add_field(name="Actions Required", 
                               value="✅ Like\n🔄 Retweet\n💭 Reply with meaningful content",
                               inline=False)

            await ctx.send(embed=raid_embed)
            
            # Schedule raid end
            self.bot.loop.create_task(self.end_raid(ctx, raid_id))

        except tweepy.TweepError as e:
            await ctx.send(f"Error accessing tweet: {str(e)}")

    @commands.command(name='join_raid')
    async def join_raid(self, ctx, raid_id: str, twitter_username: str):
        """
        Join an active raid
        Usage: !join_raid <raid_id> <your_twitter_username>
        """
        if raid_id not in self.active_raids:
            await ctx.send("Invalid raid ID or raid has ended!")
            return

        raid = self.active_raids[raid_id]
        user_id = str(ctx.author.id)

        # Check if user is on cooldown
        if user_id in self.raid_cooldowns:
            if datetime.now() < self.raid_cooldowns[user_id]:
                remaining = (self.raid_cooldowns[user_id] - datetime.now()).seconds
                await ctx.send(f"You're on raid cooldown! Try again in {remaining} seconds.")
                return

        # Add user to raid participants
        raid['participants'].add(user_id)
        self.raid_participants[user_id] = twitter_username

        await ctx.send(f"You've joined the raid! Complete the required actions on Twitter using account @{twitter_username}")

    @commands.command(name='verify_raid')
    async def verify_raid(self, ctx, raid_id: str):
        """
        Verify user's raid participation
        Usage: !verify_raid <raid_id>
        """
        if raid_id not in self.active_raids:
            await ctx.send("Invalid raid ID or raid has ended!")
            return

        raid = self.active_raids[raid_id]
        user_id = str(ctx.author.id)

        if user_id not in raid['participants']:
            await ctx.send("You haven't joined this raid!")
            return

        try:
            twitter_username = self.raid_participants[user_id]
            tweet = self.twitter_api.get_status(raid['tweet_id'])
            
            # Verify user's actions
            actions_completed = 0
            reward_earned = 0

            # Check like
            if self.verify_like(tweet.id, twitter_username):
                actions_completed += 1
                reward_earned += raid['reward']

            # Check retweet
            if self.verify_retweet(tweet.id, twitter_username):
                actions_completed += 1
                reward_earned += raid['reward']

            # Check reply
            if self.verify_reply(tweet.id, twitter_username):
                actions_completed += 1
                reward_earned += raid['reward']

            # Award VortexCoins
            if actions_completed > 0:
                guild_id = str(ctx.guild.id)
                reward_coins(guild_id, user_id, reward_earned)
                
                # Set cooldown
                self.raid_cooldowns[user_id] = datetime.now() + timedelta(hours=1)

                await ctx.send(f"Raid participation verified! You completed {actions_completed} actions and earned {reward_earned} VortexCoins!")
            else:
                await ctx.send("No raid actions verified. Make sure to like, retweet, and reply to the tweet!")

        except tweepy.TweepError as e:
            await ctx.send(f"Error verifying raid actions: {str(e)}")

    async def end_raid(self, ctx, raid_id: str):
        """
        End the raid after duration expires
        """
        raid = self.active_raids[raid_id]
        await asyncio.sleep(raid['duration'] * 60)  # Convert minutes to seconds

        try:
            tweet = self.twitter_api.get_status(raid['tweet_id'])
            
            # Calculate raid impact
            final_metrics = {
                'likes': tweet.favorite_count - raid['initial_metrics']['likes'],
                'retweets': tweet.retweet_count - raid['initial_metrics']['retweets'],
                'participants': len(raid['participants'])
            }

            # Create raid summary embed
            summary_embed = discord.Embed(
                title="📊 Raid Summary",
                description=f"Raid on {raid['tweet_url']} has ended!",
                color=discord.Color.green()
            )
            summary_embed.add_field(name="New Likes", value=final_metrics['likes'])
            summary_embed.add_field(name="New Retweets", value=final_metrics['retweets'])
            summary_embed.add_field(name="Participants", value=final_metrics['participants'])

            await ctx.send(embed=summary_embed)
            del self.active_raids[raid_id]

        except tweepy.TweepError as e:
            await ctx.send(f"Error generating raid summary: {str(e)}")

    def verify_like(self, tweet_id, username):
        """Verify if user liked the tweet"""
        try:
            likes = self.twitter_api.get_favorites(tweet_id)
            return any(like.user.screen_name.lower() == username.lower() for like in likes)
        except:
            return False

    def verify_retweet(self, tweet_id, username):
        """Verify if user retweeted the tweet"""
        try:
            retweets = self.twitter_api.get_retweets(tweet_id)
            return any(rt.user.screen_name.lower() == username.lower() for rt in retweets)
        except:
            return False

    def verify_reply(self, tweet_id, username):
        """Verify if user replied to the tweet"""
        try:
            replies = self.twitter_api.search(q=f"to:{username}", since_id=tweet_id)
            return any(reply.in_reply_to_status_id == tweet_id for reply in replies)
        except:
            return False

    @commands.command(name='raid_help')
    async def raid_help(self, ctx):
        """Display help information about raids"""
        help_embed = discord.Embed(
            title="Twitter Raid Help",
            description="Help guide for Twitter raid commands",
            color=discord.Color.blue()
        )
        help_embed.add_field(
            name="Start a Raid",
            value="!start_raid <tweet_url> [duration_in_minutes] [reward_per_action]",
            inline=False
        )
        help_embed.add_field(
            name="Join a Raid",
            value="!join_raid <raid_id> <your_twitter_username>",
            inline=False
        )
        help_embed.add_field(
            name="Verify Participation",
            value="!verify_raid <raid_id>",
            inline=False
        )
        await ctx.send(embed=help_embed)

# Governance DAO Voting System
class GovernanceDAO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.proposals = {}  # Store active and completed proposals
        self.voting_power = {}  # Store user voting power
        self.dao_settings = {
            'min_proposal_duration': 24,  # hours
            'max_proposal_duration': 168,  # hours (7 days)
            'quorum_threshold': 0.1,  # 10% of eligible voters
            'passing_threshold': 0.5,  # 50% majority
            'min_voting_power': 100,  # Minimum VortexCoins to vote
            'proposal_fee': 1000  # Cost to create a proposal
        }
        self.voting_roles = ['DAO Member', 'Governor', 'Admin']  # Roles that can vote

    def calculate_voting_power(self, user_id, guild_id):
        """Calculate user's voting power based on VortexCoins and roles"""
        base_power = vortex_coins.get(guild_id, {}).get(user_id, 0)
        
        # Get user's roles for multiplier
        guild = self.bot.get_guild(int(guild_id))
        if guild:
            member = guild.get_member(int(user_id))
            if member:
                role_multiplier = 1.0
                for role in member.roles:
                    if role.name in ['Governor']:
                        role_multiplier = 2.0
                    elif role.name in ['DAO Member']:
                        role_multiplier = 1.5
                
                return int(base_power * role_multiplier)
        
        return base_power

    @commands.command(name='create_proposal')
    async def create_proposal(self, ctx, title: str, duration: int, *, description: str):
        """
        Create a new governance proposal
        Usage: !create_proposal <title> <duration_hours> <description>
        """
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        # Check if user has enough VortexCoins for proposal fee
        user_balance = vortex_coins.get(guild_id, {}).get(user_id, 0)
        if user_balance < self.dao_settings['proposal_fee']:
            await ctx.send(f"You need {self.dao_settings['proposal_fee']} VortexCoins to create a proposal!")
            return
        
        # Validate duration
        if duration < self.dao_settings['min_proposal_duration'] or duration > self.dao_settings['max_proposal_duration']:
            await ctx.send(f"Duration must be between {self.dao_settings['min_proposal_duration']} and {self.dao_settings['max_proposal_duration']} hours!")
            return
        
        # Check if user has voting power
        voting_power = self.calculate_voting_power(user_id, guild_id)
        if voting_power < self.dao_settings['min_voting_power']:
            await ctx.send(f"You need at least {self.dao_settings['min_voting_power']} voting power to create proposals!")
            return
        
        # Deduct proposal fee
        vortex_coins[guild_id][user_id] -= self.dao_settings['proposal_fee']
        
        # Create proposal
        proposal_id = len(self.proposals) + 1
        self.proposals[proposal_id] = {
            'id': proposal_id,
            'title': title,
            'description': description,
            'author': user_id,
            'author_name': ctx.author.display_name,
            'guild_id': guild_id,
            'created_at': datetime.now(),
            'duration': duration,
            'status': 'active',
            'votes': {'yes': {}, 'no': {}, 'abstain': {}},
            'total_voting_power': 0,
            'quorum_met': False,
            'passed': False
        }
        
        # Create proposal embed
        embed = discord.Embed(
            title=f"🗳️ New DAO Proposal #{proposal_id}",
            description=f"**{title}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="Author", value=ctx.author.display_name, inline=True)
        embed.add_field(name="Duration", value=f"{duration} hours", inline=True)
        embed.add_field(name="Status", value="🟢 Active", inline=True)
        embed.add_field(name="Voting Power Required", value=f"{self.dao_settings['min_voting_power']}+", inline=True)
        embed.add_field(name="Quorum Threshold", value=f"{self.dao_settings['quorum_threshold']*100}%", inline=True)
        embed.add_field(name="Passing Threshold", value=f"{self.dao_settings['passing_threshold']*100}%", inline=True)
        
        proposal_msg = await ctx.send(embed=embed)
        
        # Add voting reactions
        await proposal_msg.add_reaction('✅')  # Yes
        await proposal_msg.add_reaction('❌')  # No
        await proposal_msg.add_reaction('🤷')  # Abstain
        
        # Store message ID for tracking
        self.proposals[proposal_id]['message_id'] = proposal_msg.id
        self.proposals[proposal_id]['channel_id'] = ctx.channel.id
        
        # Schedule proposal end
        self.bot.loop.create_task(self.end_proposal(proposal_id, duration))
        
        await ctx.send(f"Proposal #{proposal_id} created successfully! Voting is now open for {duration} hours.")

    @commands.command(name='vote')
    async def vote(self, ctx, proposal_id: int, choice: str):
        """
        Vote on a proposal
        Usage: !vote <proposal_id> <yes/no/abstain>
        """
        if proposal_id not in self.proposals:
            await ctx.send("Invalid proposal ID!")
            return
        
        proposal = self.proposals[proposal_id]
        
        if proposal['status'] != 'active':
            await ctx.send("This proposal is no longer active!")
            return
        
        # Check if user has voting power
        user_id = str(ctx.author.id)
        voting_power = self.calculate_voting_power(user_id, proposal['guild_id'])
        
        if voting_power < self.dao_settings['min_voting_power']:
            await ctx.send(f"You need at least {self.dao_settings['min_voting_power']} voting power to vote!")
            return
        
        # Check if user has already voted
        if user_id in proposal['votes']['yes'] or user_id in proposal['votes']['no'] or user_id in proposal['votes']['abstain']:
            await ctx.send("You have already voted on this proposal!")
            return
        
        # Validate choice
        choice = choice.lower()
        if choice not in ['yes', 'no', 'abstain']:
            await ctx.send("Invalid choice! Use: yes, no, or abstain")
            return
        
        # Record vote
        proposal['votes'][choice][user_id] = voting_power
        
        # Update total voting power
        proposal['total_voting_power'] = sum(
            sum(votes.values()) for votes in proposal['votes'].values()
        )
        
        await ctx.send(f"Vote recorded! You voted **{choice}** with {voting_power} voting power.")

    @commands.command(name='proposal_status')
    async def proposal_status(self, ctx, proposal_id: int):
        """
        Check the status of a proposal
        Usage: !proposal_status <proposal_id>
        """
        if proposal_id not in self.proposals:
            await ctx.send("Invalid proposal ID!")
            return
        
        proposal = self.proposals[proposal_id]
        
        # Calculate vote totals
        yes_votes = sum(proposal['votes']['yes'].values())
        no_votes = sum(proposal['votes']['no'].values())
        abstain_votes = sum(proposal['votes']['abstain'].values())
        total_votes = yes_votes + no_votes + abstain_votes
        
        # Calculate percentages
        yes_percentage = (yes_votes / total_votes * 100) if total_votes > 0 else 0
        no_percentage = (no_votes / total_votes * 100) if total_votes > 0 else 0
        
        # Check quorum and passing status
        guild = self.bot.get_guild(int(proposal['guild_id']))
        eligible_voters = 0
        if guild:
            for member in guild.members:
                if any(role.name in self.voting_roles for role in member.roles):
                    eligible_voters += 1
        
        quorum_met = total_votes >= (eligible_voters * self.dao_settings['quorum_threshold'])
        passed = yes_percentage > (self.dao_settings['passing_threshold'] * 100) and quorum_met
        
        # Create status embed
        embed = discord.Embed(
            title=f"📊 Proposal #{proposal_id} Status",
            description=f"**{proposal['title']}**",
            color=discord.Color.green() if passed else discord.Color.red()
        )
        
        embed.add_field(name="Status", value=proposal['status'].title(), inline=True)
        embed.add_field(name="Author", value=proposal['author_name'], inline=True)
        embed.add_field(name="Created", value=proposal['created_at'].strftime("%Y-%m-%d %H:%M"), inline=True)
        
        embed.add_field(name="Yes Votes", value=f"{yes_votes} ({yes_percentage:.1f}%)", inline=True)
        embed.add_field(name="No Votes", value=f"{no_votes} ({no_percentage:.1f}%)", inline=True)
        embed.add_field(name="Abstain", value=f"{abstain_votes}", inline=True)
        
        embed.add_field(name="Total Voting Power", value=f"{total_votes}", inline=True)
        embed.add_field(name="Quorum Met", value="✅" if quorum_met else "❌", inline=True)
        embed.add_field(name="Passing", value="✅" if passed else "❌", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='list_proposals')
    async def list_proposals(self, ctx, status: str = 'active'):
        """
        List all proposals
        Usage: !list_proposals [active/completed/all]
        """
        if status not in ['active', 'completed', 'all']:
            await ctx.send("Invalid status! Use: active, completed, or all")
            return
        
        filtered_proposals = []
        for proposal in self.proposals.values():
            if status == 'all' or proposal['status'] == status:
                filtered_proposals.append(proposal)
        
        if not filtered_proposals:
            await ctx.send(f"No {status} proposals found!")
            return
        
        embed = discord.Embed(
            title=f"📋 {status.title()} Proposals",
            color=discord.Color.blue()
        )
        
        for proposal in filtered_proposals[-10:]:  # Show last 10
            status_emoji = "🟢" if proposal['status'] == 'active' else "🔴"
            embed.add_field(
                name=f"{status_emoji} Proposal #{proposal['id']}: {proposal['title']}",
                value=f"Author: {proposal['author_name']} | Status: {proposal['status'].title()}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='my_voting_power')
    async def my_voting_power(self, ctx):
        """
        Check your current voting power
        Usage: !my_voting_power
        """
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        voting_power = self.calculate_voting_power(user_id, guild_id)
        base_balance = vortex_coins.get(guild_id, {}).get(user_id, 0)
        
        # Get role multiplier
        role_multiplier = 1.0
        role_name = "Member"
        guild = self.bot.get_guild(int(guild_id))
        if guild:
            member = guild.get_member(int(user_id))
            if member:
                for role in member.roles:
                    if role.name in ['Governor']:
                        role_multiplier = 2.0
                        role_name = "Governor"
                    elif role.name in ['DAO Member']:
                        role_multiplier = 1.5
                        role_name = "DAO Member"
        
        embed = discord.Embed(
            title=f"🗳️ {ctx.author.display_name}'s Voting Power",
            color=discord.Color.blue()
        )
        embed.add_field(name="Base Balance", value=f"{base_balance} VortexCoins", inline=True)
        embed.add_field(name="Role", value=role_name, inline=True)
        embed.add_field(name="Role Multiplier", value=f"{role_multiplier}x", inline=True)
        embed.add_field(name="Total Voting Power", value=f"{voting_power}", inline=True)
        embed.add_field(name="Can Vote", value="✅" if voting_power >= self.dao_settings['min_voting_power'] else "❌", inline=True)
        embed.add_field(name="Can Create Proposals", value="✅" if voting_power >= self.dao_settings['min_voting_power'] else "❌", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='dao_settings')
    @commands.has_role('Admin')
    async def dao_settings(self, ctx):
        """
        View current DAO settings (Admin only)
        Usage: !dao_settings
        """
        embed = discord.Embed(
            title="⚙️ DAO Settings",
            color=discord.Color.gold()
        )
        
        for setting, value in self.dao_settings.items():
            if isinstance(value, float):
                value = f"{value*100}%"
            elif setting in ['min_proposal_duration', 'max_proposal_duration']:
                value = f"{value} hours"
            embed.add_field(name=setting.replace('_', ' ').title(), value=value, inline=True)
        
        embed.add_field(name="Voting Roles", value=", ".join(self.voting_roles), inline=False)
        
        await ctx.send(embed=embed)

    async def end_proposal(self, proposal_id: int, duration_hours: int):
        """
        End a proposal after its duration expires
        """
        await asyncio.sleep(duration_hours * 3600)  # Convert hours to seconds
        
        if proposal_id not in self.proposals:
            return
        
        proposal = self.proposals[proposal_id]
        proposal['status'] = 'completed'
        
        # Calculate final results
        yes_votes = sum(proposal['votes']['yes'].values())
        no_votes = sum(proposal['votes']['no'].values())
        abstain_votes = sum(proposal['votes']['abstain'].values())
        total_votes = yes_votes + no_votes + abstain_votes
        
        # Check quorum and passing status
        guild = self.bot.get_guild(int(proposal['guild_id']))
        eligible_voters = 0
        if guild:
            for member in guild.members:
                if any(role.name in self.voting_roles for role in member.roles):
                    eligible_voters += 1
        
        quorum_met = total_votes >= (eligible_voters * self.dao_settings['quorum_threshold'])
        yes_percentage = (yes_votes / total_votes * 100) if total_votes > 0 else 0
        passed = yes_percentage > (self.dao_settings['passing_threshold'] * 100) and quorum_met
        
        proposal['quorum_met'] = quorum_met
        proposal['passed'] = passed
        
        # Send final results
        channel = self.bot.get_channel(proposal['channel_id'])
        if channel:
            embed = discord.Embed(
                title=f"🏁 Proposal #{proposal_id} Results",
                description=f"**{proposal['title']}**",
                color=discord.Color.green() if passed else discord.Color.red()
            )
            
            embed.add_field(name="Final Status", value="✅ PASSED" if passed else "❌ FAILED", inline=True)
            embed.add_field(name="Quorum Met", value="✅" if quorum_met else "❌", inline=True)
            embed.add_field(name="Total Voting Power", value=f"{total_votes}", inline=True)
            
            embed.add_field(name="Yes Votes", value=f"{yes_votes} ({yes_percentage:.1f}%)", inline=True)
            embed.add_field(name="No Votes", value=f"{no_votes} ({100-yes_percentage:.1f}%)", inline=True)
            embed.add_field(name="Abstain", value=f"{abstain_votes}", inline=True)
            
            await channel.send(embed=embed)

    @commands.command(name='dao_help')
    async def dao_help(self, ctx):
        """
        Display help for DAO commands
        Usage: !dao_help
        """
        help_embed = discord.Embed(
            title="🗳️ DAO Governance Help",
            description="Commands for participating in DAO governance",
            color=discord.Color.blue()
        )
        
        help_embed.add_field(
            name="Creating Proposals",
            value="`!create_proposal <title> <duration_hours> <description>`\nCreate a new governance proposal",
            inline=False
        )
        
        help_embed.add_field(
            name="Voting",
            value="`!vote <proposal_id> <yes/no/abstain>`\nVote on an active proposal",
            inline=False
        )
        
        help_embed.add_field(
            name="Information",
            value="`!proposal_status <proposal_id>` - Check proposal status\n"
                  "`!list_proposals [active/completed/all]` - List proposals\n"
                  "`!my_voting_power` - Check your voting power",
            inline=False
        )
        
        help_embed.add_field(
            name="Requirements",
            value=f"• Minimum {self.dao_settings['min_voting_power']} VortexCoins to vote\n"
                  f"• {self.dao_settings['proposal_fee']} VortexCoins to create proposals\n"
                  f"• {self.dao_settings['quorum_threshold']*100}% quorum required\n"
                  f"• {self.dao_settings['passing_threshold']*100}% majority to pass",
            inline=False
        )
        
        await ctx.send(embed=help_embed)

# manage contributions

# Add to bot setup

bot.add_cog(TwitterRaiding(bot))
bot.add_cog(GovernanceDAO(bot))
