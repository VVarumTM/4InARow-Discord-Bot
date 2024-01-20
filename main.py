import discord
from discord.ext import commands
import time

# Discord
TOKEN = # Your Bot Token
channel_id = # Your Channel Id

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='.', intents=intents)

# Variables
counter = 0
player_1 = None
player_2 = None
drawing = None
running = False   # boolean - tells if game is running (true/false)
turn = 1


# As soon as the bot starts:
@client.event
async def on_ready():
    # it needs the channel_id
    channel = client.get_channel(channel_id)

    await channel.send("Im online now! A new session has begun! To start a game, use:  .new ")


@client.command()
async def new(ctx):
    # it needs the channel_id
    channel = client.get_channel(channel_id)
    global running

    if not running:
        running = True

        # button
        view = discord.ui.View()

        # This happens, as soon, as the button1 is clicked
        async def button1_callback(interaction: discord.Interaction):
            global player_1, player_2

            if player_1 == None:
                # the user mustn't already be taken
                player_1 = interaction.user
                # making the button green
                button1.style = discord.ButtonStyle.success
                # making only button1 work
                button1.disabled = True
                button2.disabled = False
                # telling the user he is player 1
                time.sleep(1)
                await welcome.edit(content=f"  {player_1.mention}, you are player 1!\n", view=view)

    # This happens, as soon, as the button1 is clicked
        async def button2_callback(interaction: discord.Interaction):
            global player_1, player_2, board, turn, drawing

            # player 2 mustn't be player 1
            if player_2 is None and player_1 != interaction.user:
                player_2 = interaction.user
                # making the button green
                button2.style = discord.ButtonStyle.success
                # disabling button 2
                button2.disabled = True
                # telling user 2 he is player 2
                time.sleep(1)
                await welcome.edit(content=f"  {player_2.mention}, you are now player 2!", view=view)

                # Remove welcome message
                time.sleep(1)
                await welcome.delete()

                # setting the turn
                turn = 1
                board = Board(channel)

                drawing = await channel.send("·")
                await board.draw_board()
                # deleting text
                view.clear_items()

        # creating buttons
        button1 = discord.ui.Button(label="Player 1", style=discord.ButtonStyle.primary, disabled=False)
        button2 = discord.ui.Button(label="Player 2", style=discord.ButtonStyle.primary, disabled=True)
        button1.callback = button1_callback
        button2.callback = button2_callback
        view.add_item(button1)
        view.add_item(button2)

        # sending the welcome message
        welcome = await channel.send(content="_\n"
                                             "Click on Player 1! \n", view=view)


@client.command()
async def p(ctx, message):
    global board, player_1, player_2
    message = int(message) - 1

    if ((player_1 == ctx.message.author and board.turn == 1) or (
            player_2 == ctx.message.author and board.turn == -1)) and not board.gameover:
        await board.place(message, ctx)
    else:
        if not board.gameover:
            bot_message = await ctx.channel.send("its not your turn")
            time.sleep(1)
            await bot_message.delete()


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await client.process_commands(message)
    await message.delete()


def vertical_win(x, turn, board):
    streak = 0
    for field in board[x]:
        if turn == field:
            streak += 1
            if streak == 4:
                return True
        else:
            streak = 0
    return False


def horizontal_win(y, turn, board):
    streak = 0
    for x in range(7):
        if turn == board[x][y]:
            streak += 1
            if streak == 4:
                return True
        else:
            streak = 0
    return False


def diagonal_a_win(turn, board):
    streak = 0
    for start_field in start_field_list_a:
        x = start_field[1]
        y = start_field[0]
        while (x <= 6) and (y <= 5):
            if turn == board[x][y]:
                streak += 1
                if streak == 4:
                    return True
            else:
                streak = 0
            x += 1
            y += 1
    return False


def diagonal_b_win(turn, board):
    streak = 0
    for start_field in start_field_list_b:
        x = start_field[1]
        y = start_field[0]
        while (x <= 6) and (y <= 5):
            if turn == board[x][y]:
                streak += 1
                if streak == 4:
                    return True
            else:
                streak = 0
            x -= 1
            y += 1
    return False


pieces = {
    0: "⚫",
    1: "🟡",
    -1: "🔴"
}

start_field_list_a = [[0, 0], [0, 1], [0, 2], [1, 0], [2, 0], [3, 0]]
start_field_list_b = [[0, 3], [0, 4], [0, 5], [0, 6], [1, 6], [2, 6]]


# Main
class Board:
    def __init__(self, channel):
        self.gameover = False
        self.turn = 1
        self.board = [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
        self.channel = channel

    async def place(self, position, ctx):
        # Check if Number in board
        if position not in range(7):
            await self.channel.send("your number is off the board")
        else:
            height = len([x for x in self.board[position] if x != 0])
            if height > 5:
                await self.channel.send("This row is already full, retry!")
            else:
                self.board[position][height] = self.turn
                await self.game_win(height, position, ctx)
                await self.draw_board()
                self.turn *= -1

    async def draw_board(self):
        board_string = ". \n" \
                       "｜  1     2    3   4    5    6    7  ｜\n" \
                       f"｜{pieces[self.board[0][5]]}{pieces[self.board[1][5]]}{pieces[self.board[2][5]]}{pieces[self.board[3][5]]}{pieces[self.board[4][5]]}{pieces[self.board[5][5]]}{pieces[self.board[6][5]]}｜\n" \
                       f"｜{pieces[self.board[0][4]]}{pieces[self.board[1][4]]}{pieces[self.board[2][4]]}{pieces[self.board[3][4]]}{pieces[self.board[4][4]]}{pieces[self.board[5][4]]}{pieces[self.board[6][4]]}｜\n" \
                       f"｜{pieces[self.board[0][3]]}{pieces[self.board[1][3]]}{pieces[self.board[2][3]]}{pieces[self.board[3][3]]}{pieces[self.board[4][3]]}{pieces[self.board[5][3]]}{pieces[self.board[6][3]]}｜\n" \
                       f"｜{pieces[self.board[0][2]]}{pieces[self.board[1][2]]}{pieces[self.board[2][2]]}{pieces[self.board[3][2]]}{pieces[self.board[4][2]]}{pieces[self.board[5][2]]}{pieces[self.board[6][2]]}｜\n" \
                       f"｜{pieces[self.board[0][1]]}{pieces[self.board[1][1]]}{pieces[self.board[2][1]]}{pieces[self.board[3][1]]}{pieces[self.board[4][1]]}{pieces[self.board[5][1]]}{pieces[self.board[6][1]]}｜\n" \
                       f"｜{pieces[self.board[0][0]]}{pieces[self.board[1][0]]}{pieces[self.board[2][0]]}{pieces[self.board[3][0]]}{pieces[self.board[4][0]]}{pieces[self.board[5][0]]}{pieces[self.board[6][0]]}｜\n" \
                       "  `‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾´"

        global drawing
        await drawing.edit(content=board_string)

    async def game_win(self, height, position, ctx):
        global running, player_2, player_1
        if horizontal_win(height, self.turn, self.board) \
                or vertical_win(position, self.turn, self.board) \
                or diagonal_a_win(self.turn, self.board) \
                or diagonal_b_win(self.turn, self.board):
            self.gameover = True
            if ctx.message.author == player_1:
                await self.channel.send(f"congrats, {player_1.mention} YOU WON against {player_2.mention}\n"
                                        f"To play a new round, use .new again!")
            else:
                await self.channel.send(f"congrats, {player_2.mention} YOU WON against {player_1.mention}\n"
                                        f"To play a new round, use .new again!")

            running = False
            player_2 = None
            player_1 = None


board = Board(client.get_channel(channel_id))

client.run(TOKEN)