from aiogram import types, Router, F, Bot
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

from filters.chat_types import ChatTypeFilter
from keyboards import reply


import os
from dotenv import find_dotenv, load_dotenv

from my_func import check_text, decor_text_for_word

load_dotenv(find_dotenv())

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(
    or_f(CommandStart(), (F.text.lower().contains('в начало') | (F.text.lower().contains('нет')))))
async def start_cmd(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await message.answer(os.getenv('START_WORDS'), reply_markup=reply.start_kb)


@user_private_router.message(or_f(Command('donate'), (F.text.lower().contains('поддержать авторов'))))
async def donate_cmd(message: types.Message):
    text = as_list(
        as_marked_section(
            Bold('Способы поддержки:'),
            Italic("BelinvestBank: ") + " 234324234324",
            marker='✅',
        ),
        as_marked_section(
            Bold("В процессе добавления:"),
            Italic("QIWI Кошелек"),
            Italic("Криптовалюта"),
            marker='❎'
        ),
        sep='\n-----------------------\n'
    )
    await message.answer(text.as_html(), reply_markup=reply.back_to_start)


@user_private_router.message(Command('about'))
async def about_cmd(message: types.Message):
    await message.answer('О нас:', reply_markup=reply.back_to_start)


@user_private_router.message(Command('secret'))
async def secret_cmd(message: types.Message):
    await message.answer('Ты сделал домашку от Тайлера?', reply_markup=reply.back_to_start)


# Код ниже состояния диалога по кнопке "Проверить орфографию"

class AddTextOrDocument(StatesGroup):
    text = State()


@user_private_router.message(StateFilter(None),
                             F.text.lower().contains("проверить орфографию") | F.text.lower().contains("да"))
async def spelling_cmd(message: types.Message, state: FSMContext):
    await message.answer('Вставте в чат нужный текст или отправтье Word файл😊', reply_markup=reply.back_to_start)
    await state.set_state(AddTextOrDocument.text)


@user_private_router.message(AddTextOrDocument.text, F.text | F.document)
async def spelling_2_cmd(message: types.Message, bot: Bot, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()

    if data['text'] is None:
        await state.update_data(text=message.document)
        data = await state.get_data()

    if isinstance(data['text'], str):
        res = check_text(data['text'])
        if isinstance(res, str):
            await message.answer(res)
        else:
            await message.answer(f"Исправленный текcт:\n\n{res[0]}")
            await message.answer(f"Исправления:\n\n{res[1]}")
    else:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, "text.doc")   # TODO
        await message.answer('В процессе разработки')
    await state.clear()
    await message.answer('Хотите продолжить?', reply_markup=reply.yes_or_no)


# Код ниже состояния диалога по кнопке "Проверить орформление"
class AddTextOrDocumentForDecor(StatesGroup):
    text = State()
    text_size = State()
    font = State()

    texts = {
        'AddTextOrDocumentForDecor:text': 'Введите в чат нужный текст или Word файл заново:',
        'AddTextOrDocumentForDecor:text_size': 'Введите размер текста заново:',
        'AddTextOrDocumentForDecor:font': 'Введите нужный шрифт заново:',
    }

@user_private_router.message(F.text.lower().contains("проверить оформление"))
async def decor_cmd(message: types.Message, state: FSMContext):
    await message.answer('Вставте в чат нужный текст или отправтье Word файл😊', reply_markup=reply.back_to_start)
    await state.set_state(AddTextOrDocumentForDecor.text)


#Вернутся на шаг назад (на прошлое состояние)
@user_private_router.message(StateFilter('*'), F.text.lower().contains("вернуться назад"))
async def back_step_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state is None:
        return await state.set_state(AddTextOrDocumentForDecor.text)

    previous = None
    for step in AddTextOrDocumentForDecor.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            if previous is None:
                return await state.set_state(AddTextOrDocumentForDecor.text)
            await message.answer(f"Вы вернулись к прошлому шагу \n\n<b>{AddTextOrDocumentForDecor.texts[previous.state]}</b>")
            return
        previous = step


@user_private_router.message(AddTextOrDocumentForDecor.text, F.text | F.document)
async def decor_2_cmd(message: types.Message, state: FSMContext):
    await message.answer('Какой размер текста вам нужен?😊', reply_markup=reply.back_to_start_and_back)
    await state.update_data(text=message.text)
    data_0 = await state.get_data()
    if data_0['text'] is None:
        await state.update_data(text=message.document)
        document = message.document
        print(document)
    await state.set_state(AddTextOrDocumentForDecor.text_size)


@user_private_router.message(AddTextOrDocumentForDecor.text_size, F.text)
async def decor_3_cmd(message: types.Message, state: FSMContext):
    await message.answer('Какой шрифт вам нужен?😊', reply_markup=reply.back_to_start_and_back)
    await state.update_data(text_size=message.text)
    await state.set_state(AddTextOrDocumentForDecor.font)


@user_private_router.message(AddTextOrDocumentForDecor.font, F.text)
async def decor_4_cmd(message: types.Message, state: FSMContext):
    await state.update_data(font=message.text)
    data = await state.get_data()
    print(data)
    if isinstance(data['text'], str):
        decor_text_for_word(data['text'], int(data['text_size']), data['font'])
        file_path = r'/Users/mrkot/Desktop/telegram-bot/example.docx'
        await message.answer_document(document=types.FSInputFile(path=file_path, filename='example'))
        os.remove(path=file_path)
    else:
        await message.answer('В процессе разработки')
    await state.clear()
    await message.answer('Хотите продолжить?', reply_markup=reply.yes_or_no)


@user_private_router.edited_message(F.text)
async def edit_cmd(message: types.Message):
    await message.answer('Это исправленное сообщение!')


@user_private_router.message()
async def cmd(message: types.Message):
    await message.answer('Пожалуйста, выберите корректный пункт меню.')
