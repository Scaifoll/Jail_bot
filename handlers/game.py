from aiogram import types, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

GRID_SIZE = 5
MAX_SHIPS = 3
CELL_EMPTY = "⬜"
CELL_SHIP = "🚢"
CELL_HIT = "💥"
CELL_MISS = "❌"

class BattleshipStates(StatesGroup):
    waiting_for_opponent = State()
    placing_ships = State()
    in_battle = State()

# Структура игры
games = {}

def get_keyboard(game, player_id, reveal_ships=False):
    """
    Строим клавиатуру для игрока.
    Если reveal_ships=True — показываем свои корабли.
    Если False — показываем только свои выстрелы по противнику (скрывая корабли).
    """
    builder = InlineKeyboardBuilder()
    player_data = game['players'][player_id]

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if reveal_ships:
                # Показываем корабли своего поля
                if (row, col) in player_data['ships']:
                    emoji = CELL_SHIP
                else:
                    emoji = CELL_EMPTY
            else:
                # Показываем только куда стрелял по противнику
                cell = player_data['enemy_shots'].get((row, col))
                if cell == 'hit':
                    emoji = CELL_HIT
                elif cell == 'miss':
                    emoji = CELL_MISS
                else:
                    emoji = CELL_EMPTY
            builder.button(text=emoji, callback_data=f"bs:{game['id']}:{player_id}:{row}:{col}")
        builder.adjust(GRID_SIZE)
    return builder.as_markup()

async def start_battleship(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    # Создаем новую игру с уникальным id = user_id (пока что для простоты)
    game_id = str(user_id)
    if game_id in games:
        await message.answer("Игра уже создана, ждём оппонента /join")
        return

    games[game_id] = {
        'id': game_id,
        'players': {
            user_id: {
                'ships': set(),
                'enemy_shots': {},  # Где противник стрелял
                'own_message_id': None,
                'enemy_message_id': None,
                'ready': False,
                'turn': False,
            }
        },
        'state': 'waiting_for_opponent',
        'turn_player': None,
        'waiting_player': None,
    }

    await state.set_state(BattleshipStates.waiting_for_opponent)
    await message.answer("Игра создана! Ждем оппонента, чтобы присоединиться отправь /join_game")

def get_keyboard_for_enemy(game, player_id):
    """
    Клавиатура с полем противника: показываем куда стрелял игрок и результат (попадание/промах),
    но НЕ показываем расположение кораблей.
    """
    builder = InlineKeyboardBuilder()
    player_data = game['players'][player_id]
    opponent_id = [pid for pid in game['players'] if pid != player_id][0]
    opponent_data = game['players'][opponent_id]

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pos = (row, col)
            shot_result = player_data['enemy_shots'].get(pos)
            if shot_result == 'hit':
                emoji = CELL_HIT
            elif shot_result == 'miss':
                emoji = CELL_MISS
            else:
                emoji = CELL_EMPTY
            builder.button(text=emoji, callback_data=f"bs:{game['id']}:{player_id}:{row}:{col}")
        builder.adjust(GRID_SIZE)
    return builder.as_markup()


async def join_game(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    # Ищем игру в ожидании оппонента
    game_to_join = None
    for game in games.values():
        if game['state'] == 'waiting_for_opponent' and len(game['players']) == 1:
            game_to_join = game
            break

    if not game_to_join:
        await message.answer("Нет доступных игр для присоединения. Создайте игру командой /start_game")
        return

    # Добавляем второго игрока
    game_to_join['players'][user_id] = {
        'ships': set(),
        'enemy_shots': {},
        'own_message_id': None,
        'enemy_message_id': None,
        'ready': False,
        'turn': False,
    }

    game_to_join['state'] = 'placing_ships'
    game_to_join['turn_player'] = list(game_to_join['players'].keys())[0]  # Кто первый ходит — первый игрок

    # Отправляем сообщения обоим игрокам
    for pid in game_to_join['players']:
        # Сообщение с собственным полем (показываем свои корабли)
        text_own = f"🚢 Игрок {pid}, расставьте свои {MAX_SHIPS} корабля на поле {GRID_SIZE}x{GRID_SIZE}"
        keyboard_own = get_keyboard(game_to_join, pid, reveal_ships=True)
        sent_own = await message.bot.send_message(pid, text_own, reply_markup=keyboard_own)

        # Сообщение с полем противника (куда стрелял игрок)
        text_enemy = "Поле противника"
        keyboard_enemy = get_keyboard_for_enemy(game_to_join, pid)
        sent_enemy = await message.bot.send_message(pid, text_enemy, reply_markup=keyboard_enemy)

        # Сохраняем id сообщений для последующего редактирования
        game_to_join['players'][pid]['own_message_id'] = sent_own.message_id
        game_to_join['players'][pid]['enemy_message_id'] = sent_enemy.message_id

    await state.clear()
    await message.answer("Вы присоединились к игре! Расставьте корабли.")

async def cell_pressed(callback: types.CallbackQuery):
    data = callback.data.split(":")
    if len(data) != 5:
        return await callback.answer()

    _, game_id, player_id_str, row_str, col_str = data
    player_id = int(player_id_str)
    row = int(row_str)
    col = int(col_str)

    user_id = callback.from_user.id

    if game_id not in games:
        return await callback.answer("Игра не найдена")

    game = games[game_id]

    if user_id not in game['players']:
        return await callback.answer("Вы не участник этой игры")

    player = game['players'][user_id]
    opponent_id = [pid for pid in game['players'] if pid != user_id][0]
    opponent = game['players'][opponent_id]

    if game['state'] == 'placing_ships':
        # Размещение кораблей игроком
        if user_id != player_id:
            return await callback.answer("Это не ваше поле!")

        pos = (row, col)
        if pos in player['ships']:
            player['ships'].remove(pos)
        elif len(player['ships']) < MAX_SHIPS:
            player['ships'].add(pos)
        else:
            return await callback.answer("Максимум кораблей установлен")

        # Обновляем клавиатуру с кораблями
        text = f"🚢 Расставьте свои корабли\nОсталось: {MAX_SHIPS - len(player['ships'])}"
        if len(player['ships']) == MAX_SHIPS:
            player['ready'] = True
            text = "✅ Все корабли размещены, ждём соперника..."

        keyboard = get_keyboard(game, user_id, reveal_ships=True)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()

        # Если оба готовы — начинаем игру
        if all(p['ready'] for p in game['players'].values()):
            game['state'] = 'in_battle'
            game['players'][game['turn_player']]['turn'] = True

            for pid in game['players']:
                text = f"🔥 Игра началась! {'Ваш ход' if pid == game['turn_player'] else 'Ход соперника'}"
                keyboard = get_keyboard(game, pid, reveal_ships=False)
                await callback.bot.edit_message_text(
                    text=text,
                    chat_id=pid,
                    message_id=game['players'][pid]['message_id'],
                    reply_markup=keyboard
                )

    elif game['state'] == 'in_battle':
        if user_id != game['turn_player']:
            return await callback.answer("Сейчас не ваш ход!")

        pos = (row, col)
        if pos in opponent['enemy_shots']:
            return await callback.answer("Вы уже стреляли сюда")

        hit = pos in opponent['ships']
        opponent['enemy_shots'][pos] = 'hit' if hit else 'miss'

        # Проверка победы
        hits = [p for p, res in opponent['enemy_shots'].items() if res == 'hit']
        if set(hits) >= opponent['ships']:
            # Победа!
            text_win = "🎉 Поздравляем, вы выиграли!"
            text_lose = "😞 Вы проиграли."

            for pid in game['players']:
                msg_text = text_win if pid == user_id else text_lose
                await callback.bot.edit_message_text(
                    text=msg_text,
                    chat_id=pid,
                    message_id=game['players'][pid]['message_id'],
                    reply_markup=None
                )
            games.pop(game_id)  # Удаляем игру
            return await callback.answer("Вы победили!")

        # Переключаем ход
        game['turn_player'] = opponent_id
        for pid in game['players']:
            text = f"🔥 {'Ваш ход' if pid == game['turn_player'] else 'Ход соперника'}"
            keyboard = get_keyboard(game, pid, reveal_ships=False)
            await callback.bot.edit_message_text(
                text=text,
                chat_id=pid,
                message_id=game['players'][pid]['message_id'],
                reply_markup=keyboard
            )

        await callback.answer("💥 Попадание!" if hit else "❌ Мимо!")

async def cancel_game(message: types.Message):
    user_id = message.from_user.id
    to_delete = []
    for gid, game in games.items():
        if user_id in game['players']:
            to_delete.append(gid)
    for gid in to_delete:
        games.pop(gid)
    await message.answer("Все ваши игры отменены.")

def register_game_handler(dp: Dispatcher):
    dp.message.register(start_battleship, Command("start_game"))
    dp.message.register(join_game, Command("join_game"))
    dp.message.register(cancel_game, Command("cancel_game"))
    dp.callback_query.register(cell_pressed, F.data.startswith("bs:"))
