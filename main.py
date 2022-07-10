from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from database import Db
from visit_make import visitmake

TOKEN = '5389547663:AAGdDCoIsxSR3SCXiDJCrUt4B1A6DAo5BYQ'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db = Db('database.db')


class Profile(StatesGroup):
    name = State()
    city = State()
    role = State()
    year = State()
    description = State()
    superpower = State()
    photo = State()


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message):
    btn_ru = KeyboardButton('Русский')
    btn_en = KeyboardButton('English')
    menu = ReplyKeyboardMarkup(one_time_keyboard=True)
    menu.add(btn_ru, btn_en)
    await message.answer('Select language', reply_markup=menu)


@dp.message_handler(commands=['clear'])
async def clear_words(message: types.Message):
    file = open('resources/words.txt', 'r+')
    file.truncate(0)
    file.close()


@dp.message_handler(commands=['push'])
async def push_words_wait(message: types.Message):
    await message.answer('Введите список слов')


@dp.message_handler(lambda message: message.text == 'Введите список слов')
async def push_words(message: types.Message):
    file = open('resources/words.txt', 'w', encoding='utf-8')
    file.write(message.text)
    file.close()


@dp.message_handler(lambda message: message.text == 'Русский', state='*')
async def bot_start(message: types.Message):
    await message.answer('👋🏻 Привет, друг Sky World Community. Давай познакомимся?')
    await message.answer('Я Помощник SWC и сейчас я сделаю для тебя визитку партнера.')
    await message.answer('✏️ Напиши свое Имя и Фамилию👇🏻')
    await Profile.name.set()


@dp.message_handler(state=Profile.name)
async def insert_name(message: types.Message, state: FSMContext):
    await state.update_data(profile_name=message.text)
    await message.reply(f'{message.text.title()} 👌🏻 Отлично')
    await message.answer("✏️ Напиши свою страну и город 👇🏻")
    await Profile.next()
    return


@dp.message_handler(state=Profile.city)
async def insert_city(message: types.Message, state: FSMContext):
    await state.update_data(profile_city=message.text)
    await Profile.next()
    await message.answer('👌🏻 Отлично')
    await message.answer('✏️ Напиши свою роль в сообществе 👇🏻')


@dp.message_handler(state=Profile.role)
async def insert_role(message: types.Message, state: FSMContext):
    if len(message.text) < 121:
        await state.update_data(profile_role=message.text)
        await Profile.next()
    else:
        await message.answer(f'В вашем тексте {len(message.text)} символов! '
                             f'Сократите и напишите ответ текстом (до 120 символов)👇🏻 🧡')
        return
    menu1 = ReplyKeyboardMarkup(one_time_keyboard=True)
    btn_2020 = KeyboardButton('2020')
    btn_2021 = KeyboardButton('2021')
    btn_2022 = KeyboardButton('2022')
    menu1.add(btn_2020, btn_2021, btn_2022)
    await message.answer('✏️ Выбери, с какого года ты состоишь в сообществе SWC?', reply_markup=menu1)


@dp.message_handler(state=Profile.year)
async def insert_year(message: types.Message, state: FSMContext):
    await state.update_data(profile_year=message.text)
    await Profile.next()
    await message.answer('🔥 Супер!')
    await message.answer('✏️ Расскажи о себе в 3 предложениях')
    await message.answer('(!!️ максимум 120 знаков)👇🏻')


@dp.message_handler(state=Profile.description)
async def insert_description(message: types.Message, state: FSMContext):
    if len(message.text) < 121:
        await state.update_data(profile_description=message.text)
        await Profile.next()
    else:
        await message.answer(f'В вашем тексте {len(message.text)} символов! '
                             f'Сократите и напишите ответ текстом (до 120 символов)👇🏻 🧡')
        return
    await message.answer("✏️ Чем можешь помочь партнёрам по сообществу? Какая твоя суперсила?")
    await message.answer('(!!️ максимум 120 знаков)👇🏻')


@dp.message_handler(state=Profile.superpower)
async def insert_superpower(message: types.Message, state: FSMContext):
    if len(message.text) < 121:
        await state.update_data(profile_superpower=message.text)
        await Profile.next()
    else:
        await message.answer(f'В вашем тексте {len(message.text)} символов! '
                             f'Сократите и напишите ответ текстом (до 120 символов)👇🏻 🧡')
        return
    await message.answer("Пришли свою фотографию 📸")


@dp.message_handler(state=Profile.photo, content_types=['photo'])
async def insert_photo(message: types.Message, state: FSMContext):
    await message.photo[-1].download('photo_user/' + str(message.from_user.id) + '.jpg')
    await Profile.next()
    user_data = await state.get_data()
    db.create_profile(message.from_user.username, str(user_data['profile_name']),
                      str(user_data['profile_city']), user_data['profile_role'], user_data['profile_year'],
                      str(user_data['profile_description']), str(user_data['profile_superpower']),
                      'photo/' + str(message.from_user.id) + '.jpg')
    await message.answer("⏳ Пару секунд, рисую картинку 👨🏻‍🎨")
    await state.finish()
    visitmake(str(message.from_user.id), message.from_user.username, str(user_data['profile_name']),
              str(user_data['profile_city']), user_data['profile_role'], str(user_data['profile_superpower']),
              user_data['profile_year'])
    photo = open('visits/' + str(message.from_user.id) + '_visit' + '.png', 'rb')
    await message.answer('👀 Посмотри, что получилось, все ли верно?')
    await message.answer_photo(photo)
    btn_yes = KeyboardButton('Да, все верно')
    btn_no = KeyboardButton('Нет, заполнить заново')
    menu2 = ReplyKeyboardMarkup(one_time_keyboard=True)
    menu2.add(btn_yes, btn_no)
    await message.answer('✅ Если тебе нравится картинка, нажми «ДА»👇🏻', reply_markup=menu2)


@dp.message_handler(lambda message: message.text == 'Да, все верно')
async def bot_yes(message: types.Message):
    image = open('visits/' + str(message.from_user.id) + '_visit' + '.png', 'rb')
    text = '@' + message.from_user.username + ', Добро пожаловать в SWC 🧡'
    Profile.reg_event = True
    # await bot.send_photo(chat_id=-1001685968921, photo=image, caption=text)


@dp.message_handler(lambda message: message.text == 'Нет, заполнить заново')
async def bot_no(message: types.Message):
    db.delete(message.from_user.id)
    Profile.reg_event = False
    await bot_start(message)


@dp.message_handler()
async def word_finder(message: types.Message):
    if db.profile_exists(message.from_user.username) is True:
        file = open('resources/words.txt', 'r', encoding='utf-8')
        word_list = file.read().split(', ')
        mes_words = message.text.split()
        for mes_word in mes_words:
            if mes_word in word_list:
                await message.answer('+1 бал')
        file.close()
        await message.answer(db.is_admin(message.from_user.username))


executor.start_polling(dp, skip_updates=True)
