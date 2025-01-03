from discord.ext import commands
import discord
import openai
import os
import random

def setup(bot):
    @bot.event
    async def on_member_join(member):
        await member.add_roles()

    @bot.event
    async def on_member_join(member):
        channel = bot.get_channel()
        await channel.send(f'{member} wellcome!')



    @bot.command()
    async def ask(ctx, *, question):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )
        answer = response['choices'][0]['message']['content'].strip()
        await ctx.send(answer)

    @bot.command()
    async def add(ctx, a: float, b: float):
        result = a + b
        await ctx.send(f'Tổng {a} + {b} là {result}')

    @bot.command()
    async def subtract(ctx, a: float, b: float):
        result = a - b
        await ctx.send(f'Hiệu {a} - {b} là {result}')

    @bot.command()
    async def multiply(ctx, a: float, b: float):
        result = a * b
        await ctx.send(f'Tích {a} * {b} là {result}')

    @bot.command()
    async def divide(ctx, a: float, b: float):
        if b == 0:
            await ctx.send('Không thể chia cho 0.')
        else:
            result = a / b
            await ctx.send(f'Thương {a} / {b} là {result}')

    @bot.command()
    async def game(ctx):
        await ctx.send(f'Để chơi game tic-tac-toe, sử dụng lệnh !ttt')
        await ctx.send(f'Để chơi game minesweeper, sử dụng lệnh !ms "số ô" "số bom" để tạo bàn chơi và !p "dòng" "cột" để mở ô.')
        await ctx.send(f'Để chơi game blackjack, sử dụng lệnh !blackjack')

    banned_words = [] 

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if any(banned_word in message.content.lower() for banned_word in banned_words):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, cảnh cáo! Đừng nói tục chửi bậy.")
            return

        await bot.process_commands(message)

    @bot.command(name='blackjack')
    async def blackjack(ctx):
        player_hand = [deal_card(), deal_card()]
        dealer_hand = [deal_card(), deal_card()]

        games[ctx.author.id] = {'player_hand': player_hand, 'dealer_hand': dealer_hand}

        await ctx.send(display_game_state(player_hand, dealer_hand), view=BlackjackView(ctx))

    def has_any_role(member, roles):
        return any(role.name in roles for role in member.roles)
    
    @bot.command(name='ms')
    async def ms(ctx, size: int, bombs: int):
        if size * size <= bombs:
            await ctx.send("Số bom phải nhỏ hơn số ô.")
            return

        board = [['0' for _ in range(size)] for _ in range(size)]
        revealed = [['-' for _ in range(size)] for _ in range(size)]

        bomb_positions = random.sample(range(size * size), bombs)
        for pos in bomb_positions:
            row, col = divmod(pos, size)
            board[row][col] = 'B'

        for row in range(size):
            for col in range(size):
                if board[row][col] == 'B':
                    continue
                count = sum((board[r][c] == 'B') for r in range(max(0, row-1), min(size, row+2)) for c in range(max(0, col-1), min(size, col+2)))
                board[row][col] = str(count)

        games[ctx.author.id] = {'board': board, 'revealed': revealed, 'size': size}

        await ctx.send("Minesweeper game started!", view=MinesweeperView(size))


    @bot.command(name='p')
    async def p(ctx, row: int, col: int):
        game = games.get(ctx.author.id)
        if not game:
            await ctx.send("Tạo bàn chơi bằng cách sử dung lệnh !ms 'số ô' 'số bom' .")
            return

        board = game['board']
        revealed = game['revealed']
        size = game['size']

        if row < 0 or row >= size or col < 0 or col >= size:
            await ctx.send("Sai vị trí.")
            return

        if revealed[row][col] != '-':
            await ctx.send("Ô này đã được mở.")
            return

        if board[row][col] == 'B':
            board_str = '\n'.join(' '.join(row) for row in board)
            await ctx.send(f"Kết thúc! mở trúng bom\n```{board_str}```")

            games.pop(ctx.author.id)
            return

        revealed[row][col] = board[row][col]

        if board[row][col] == '0':
            to_reveal = [(row, col)]
            while to_reveal:
                r, c = to_reveal.pop()
                for nr in range(max(0, r-1), min(size, r+2)):
                    for nc in range(max(0, c-1), min(size, c+2)):
                        if revealed[nr][nc] == '-' and board[nr][nc] != 'B':
                            revealed[nr][nc] = board[nr][nc]
                            if board[nr][nc] == '0':
                                to_reveal.append((nr, nc))

        board_str = '\n'.join(' '.join(row) for row in revealed)
        await ctx.send(f'```{board_str}```')

    @bot.command()
    async def ttt(ctx, pos: int):
        global player
        if board[pos - 1] == ' ':
            board[pos - 1] = player
            winner = check_winner()
            if winner:
                await ctx.send(f'Board:\n{print_board()}\nWinner: {ctx.author.name}')
                board[:] = [' ' for _ in range(9)]
            else:
                player = 'O' if player == 'X' else 'X'
                await ctx.send(f'Board:\n{print_board()}\nNext player: {player}')
        else:
            await ctx.send('Position already taken, try again.')


    @bot.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(ctx, member: discord.Member, *, reason=None):
        allowed_roles = ["Admin", "Moderator"]  # Replace with your role names
        if not has_any_role(ctx.author, allowed_roles):
            await ctx.send("Bạn không có quyền sử dụng lệnh này.")
            return

        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked from the server.')

    @bot.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(ctx, member: discord.Member, *, reason=None):
        allowed_roles = ["Admin", "Moderator"]  # Replace with your role names
        if not has_any_role(ctx.author, allowed_roles):
            await ctx.send("Bạn không có quyền sử dụng lệnh này.")
            return

        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned from the server.')

    @bot.command(name='restrict')
    @commands.has_permissions(manage_roles=True)
    async def restrict(ctx, member: discord.Member):
        allowed_roles = ["Admin", "Moderator"]  # Replace with your role names
        if not has_any_role(ctx.author, allowed_roles):
            await ctx.send("Bạn không có quyền sử dụng lệnh này.")
            return

        guild = ctx.guild
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if not mute_role:
            mute_role = await guild.create_role(name="Muted")

            for channel in guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False, read_message_history=True, read_messages=False)

        await member.add_roles(mute_role)
        await ctx.send(f'{member.mention} has been muted.')

