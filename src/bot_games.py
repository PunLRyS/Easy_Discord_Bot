import discord
from discord.ext import commands
import random


# Blackjack game
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4

games = {}

def deal_card():
    return random.choice(deck)

def calculate_hand_value(hand):
    value = sum(card_values[card] for card in hand)
    num_aces = hand.count('A')
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1
    return value

def display_hand(player, hand):
    card_icons = {
        '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣', '10': '🔟',
        'J': '🇯', 'Q': '🇶', 'K': '🇰', 'A': '🇦'
    }
    return f"{player}'s hand: {', '.join(card_icons[card] for card in hand)} (value: {calculate_hand_value(hand)})"

def display_game_state(player_hand, dealer_hand, hide_dealer_card=True):
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand) if not hide_dealer_card else "?"
    dealer_display = f"{dealer_hand[0]}, ?" if hide_dealer_card else ', '.join(dealer_hand)

    player_hand_len = len(player_hand) * 3


    return f"```\nPlayer's hand:[{player_value}]           Dealer's hand:[{dealer_value}]\n{', '.join(player_hand)}{' ' * (31 - player_hand_len)}{dealer_display}```"     

class BlackjackView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    @discord.ui.button(label='Hit', style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = games.get(self.ctx.author.id)
        if not game:
            await interaction.response.send_message("Bạn chưa bắt đầu trò chơi. Sử dụng lệnh !blackjack để bắt đầu.", ephemeral=True)
            return

        game['player_hand'].append(deal_card())
        player_value = calculate_hand_value(game['player_hand'])

        await interaction.response.edit_message(content=display_game_state(game['player_hand'], game['dealer_hand']))

        if player_value > 21:
            await interaction.followup.send("Player busts! Dealer wins.")
            del games[self.ctx.author.id]
            self.stop()

    @discord.ui.button(label='Stand', style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = games.get(self.ctx.author.id)
        if not game:
            await interaction.response.send_message("Bạn chưa bắt đầu trò chơi. Sử dụng lệnh !blackjack để bắt đầu.", ephemeral=True)
            return

        while calculate_hand_value(game['dealer_hand']) < 17:
            game['dealer_hand'].append(deal_card())

        await interaction.response.edit_message(content=display_game_state(game['player_hand'], game['dealer_hand'], hide_dealer_card=False))

        player_value = calculate_hand_value(game['player_hand'])
        dealer_value = calculate_hand_value(game['dealer_hand'])

        if dealer_value > 21 or player_value > dealer_value:
            await interaction.followup.send("Player wins!")
        elif player_value < dealer_value:
            await interaction.followup.send("Dealer wins!")
        else:
            await interaction.followup.send("It's a tie!")

        del games[self.ctx.author.id]
        self.stop()


# Minesweeper game
games = {}

class MinesweeperButton(discord.ui.Button):
    def __init__(self, row, col):
        super().__init__(style=discord.ButtonStyle.secondary, label='-', row=row)
        self.row = row
        self.col = col

    async def callback(self, interaction: discord.Interaction):
        game = games.get(interaction.user.id)
        if not game:
            await interaction.response.send_message("You don't have an active game. Start one with !minesweeper.", ephemeral=True)
            return

        board = game['board']
        revealed = game['revealed']
        size = game['size']

        if board[self.row][self.col] == 'B':
            board_str = '\n'.join(' '.join(row) for row in board)
            await interaction.response.edit_message(content=f"Thua cuộc! bạn mở trúng bom\n```{board_str}```", view=None)
            games.pop(interaction.user.id)
            return

        revealed[self.row][self.col] = board[self.row][self.col]
        self.label = board[self.row][self.col]
        self.disabled = True

        if board[self.row][self.col] == '0':
            to_reveal = [(self.row, self.col)]
            while to_reveal:
                r, c = to_reveal.pop()
                for nr in range(max(0, r-1), min(size, r+2)):
                    for nc in range(max(0, c-1), min(size, c+2)):
                        if revealed[nr][nc] == '-' and board[nr][nc] != 'B':
                            revealed[nr][nc] = board[nr][nc]
                            if board[nr][nc] == '0':
                                to_reveal.append((nr, nc))
                            button = self.view.children[nr * size + nc]
                            button.label = board[nr][nc]
                            button.disabled = True

        await interaction.response.edit_message(view=self.view)

class MinesweeperView(discord.ui.View):
    def __init__(self, size):
        super().__init__()
        for row in range(size):
            for col in range(size):
                self.add_item(MinesweeperButton(row, col))



# Tic Tac Toe game
board = [' ' for _ in range(9)]
player = 'X'

def print_board():
    return (f'{board[0]} | {board[1]} | {board[2]}\n'
            f'---------\n'
            f'{board[3]} | {board[4]} | {board[5]}\n'
            f'---------\n'
            f'{board[6]} | {board[7]} | {board[8]}')

def check_winner():
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                      (0, 3, 6), (1, 4, 7), (2, 5, 8),
                      (0, 4, 8), (2, 4, 6)]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != ' ':
            return board[condition[0]]
    if ' ' not in board:
        return 'Tie'
    return None