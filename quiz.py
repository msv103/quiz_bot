import aiosqlite
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import Dispatcher,types
from aiogram import F
from aiogram.filters.command import Command
import questions_answers, db

# Диспетчер
dp = Dispatcher()

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()

async def get_question(message, user_id):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await db.get_quiz_index(user_id)
    correct_index = questions_answers.quiz_data[current_question_index]['correct_option']
    opts = questions_answers.quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{questions_answers.quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await db.update_quiz_index(user_id, current_question_index, 0)
    await get_question(message, user_id)

async def answer(callback: types.CallbackQuery, isTrue):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса для данного пользователя
    current_question_index = await db.get_quiz_index(callback.from_user.id)
    correct_answers = await db.get_correct_answers(callback.from_user.id)
    correct_option = questions_answers.quiz_data[current_question_index]['correct_option']

    # Отправляем в чат сообщение, что ответ верный
    if isTrue:
        await callback.message.answer(f"Верно! Ответ: {questions_answers.quiz_data[current_question_index]['options'][correct_option]}")
        correct_answers += 1
    else: 
        await callback.message.answer(f"Неправильно. Правильный ответ: {questions_answers.quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await db.update_quiz_index(callback.from_user.id, current_question_index, correct_answers)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(questions_answers.quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="Показать статистику"))
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!" ,reply_markup = builder.as_markup(resize_keyboard=True))
        current_question_index += 1

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await answer(callback, True)
    
@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await answer(callback, False)


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

            
# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

@dp.message(F.text=="Показать статистику")
async def cmd_static(message: types.Message):
    correct_answers = await db.get_correct_answers(message.from_user.id)
    current_question_index = await db.get_quiz_index(message.from_user.id)
    await message.answer(f"Результат пользователя {message.from_user.full_name} {correct_answers}/{current_question_index}")