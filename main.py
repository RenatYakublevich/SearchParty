#импорт библиотек
import asyncio #асинхроность
import logging #логирование
import datetime #работа со временем


#aiogram и всё утилиты для коректной работы с Telegram API
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
#конфиг с настройками
import config
#работа с базой данных
from database import dbworker
#задаём логи
logging.basicConfig(level=logging.INFO)

#инициализируем бота
bot = Bot(token=config.bot_token)
dp = Dispatcher(bot,storage=MemoryStorage())

#инициализируем базу данных
db = dbworker('db.db')

#кнопки
button_search = KeyboardButton('Найти хату🔍')
button_create_hata = KeyboardButton('Создать хату🏠')
button_delete_hata = KeyboardButton('Удалить хату❌')

all_btn = ReplyKeyboardMarkup()
all_btn.add(button_search,button_create_hata,button_delete_hata)

#хендлер команды /start
@dp.message_handler(commands=['start'])
async def start(message : types.Message):
	await message.answer('Привет, это ищу хату бот и тут ты легко можешь найти убежище для совместного отдыха или также разыскать однобутыльцев для вписона🍾\n',reply_markup=all_btn)
	if(not db.subscriber_exists(message.from_user.id)):
		#если юзера нет в базе добавляем его
		db.add_subscriber(message.from_user.id)
#Хендлеры для создания хаты
class CreateHata(StatesGroup):
    name = State()
    description = State()
    data = State()
    city = State()
    photo = State()
@dp.message_handler(lambda message: message.text.startswith('Создать хату🏠'))
async def create_hata(message: types.Message):
	if(not db.hata_exists(message.from_user.id)):
		await message.answer("Для того что бы создать хату нужно заполнить несколько пунктов\nДавайте начнём с названия, введите желаемое названия для вашего треп хауса😉")
		await CreateHata.name.set()
	elif(db.subscriber_exists(message.from_user.id)) :
		await message.answer('У тебя уже есть активная хата!')
@dp.message_handler(state=CreateHata.name)
async def create_hata_name(message: types.Message, state: FSMContext):
	if len(message.text) < 35: 
		await state.update_data(hata_name=message.text)
		await message.reply(message.text + ' - прекрасное название\nТеперь нужно заполнить описание👇\nбез этого никак прости :9')
		await CreateHata.next()
	else:
		await message.answer('Повторите ещё раз!')
		#прерывание функции
		return
@dp.message_handler(state=CreateHata.description)
async def create_hata_description(message: types.Message, state: FSMContext):
	if len(message.text) < 250:
		await state.update_data(hata_description=message.text)
		now = datetime.datetime.now()
		button_to_day = KeyboardButton('Сегодня')
		button_tomorrow = KeyboardButton('Завтра')
		button_after_tomorrow = KeyboardButton('Послезавтра')

		all_btn = ReplyKeyboardMarkup()
		all_btn.add(button_to_day,button_tomorrow,button_after_tomorrow)
		await message.reply('Ебнутое описание,предлагаю заполнить дату, когда пройдят твоя вечеринка с бассеином(или без:) и на этом эта мучительное заполнение закончится\nДля этого нажми на любую кнопку внизу',reply_markup=all_btn)
		await CreateHata.next()
	else:
		await message.answer('Повторите ещё раз!')
		#прерывание функции
		return
@dp.message_handler(state=CreateHata.data)
async def create_hata_data(message: types.Message, state: FSMContext):
	if message.text == 'Сегодня' or message.text == 'Завтра' or message.text == 'Послезавтра':
		await state.update_data(hata_data=message.text)
		#user_data = await state.get_data()
		#db.create_hata(message.from_user.id,str(user_data['hata_description']),str(user_data['hata_name']),str(user_data['hata_data']))
		await message.reply('Прекрасно,осталось лишь понять где находится твоё чудное место\nУкажи город, где находится твой Вписка Хаус =)')
		#await state.finish()
		await CreateHata.next()
	else:
		await message.answer('Повторите ещё раз!')
		#прерывание функции
		return
@dp.message_handler(state=CreateHata.city)
async def create_hata_city(message: types.Message, state: FSMContext):
	if len(message.text) < 35:
		await state.update_data(hata_city=message.text.lower())
		user_data = await state.get_data()
		await message.answer('Анкета успешно создана!')
		db.create_hata(message.from_user.id,str(user_data['hata_description']),str(user_data['hata_name']),str(user_data['hata_data']),str(user_data['hata_city']))
		await state.finish()
	else:
		await message.answer('Повторите ещё раз!')
		#прерывание функции
		return
@dp.message_handler(lambda message : message.text == 'Удалить хату❌')
async def delete_hata(message: types.Message):
	db.delete_hata(message.from_user.id)
	await message.answer('Ваша хата была удалена!')


#хендлер который срабатывает при непредсказуемом запросе юзера
@dp.message_handler()
async def end(message : types.Message):
	await message.answer('Я не знаю, что с этим делать 😲\nЯ просто напомню, что есть команда /help =)',parse_mode=ParseMode.MARKDOWN)


#запуск полинга бота		
executor.start_polling(dp, skip_updates=True)
