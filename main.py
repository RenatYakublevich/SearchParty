#импорт библиотек
import asyncio #асинхроность
import logging #логирование
import datetime
from datetime import timedelta  #работа со временем
import random
#работа с кастом названиями
import custom_answer


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

#кнопка для отмены
button_close = KeyboardButton('Отменить❌')

close_btn = ReplyKeyboardMarkup(one_time_keyboard=True)

#хендлер команды /start
@dp.message_handler(commands=['start'],state='*')
async def start(message : types.Message):
	#кнопки для меню
	button_search = KeyboardButton('Найти хату🔍')
	button_create_hata = KeyboardButton('Создать хату🏠')
	button_delete_hata = KeyboardButton('Удалить хату❌')

	all_btn = ReplyKeyboardMarkup(one_time_keyboard=True)

	if db.hata_exists(message.from_user.id):

		all_btn.add(button_search,button_create_hata,button_delete_hata)
	else:
		all_btn.add(button_search,button_create_hata)

	await message.answer('Привет, это ищу хату бот и тут ты легко можешь найти убежище для совместного отдыха или также разыскать однобутыльцев для вписона🍾\n',reply_markup=all_btn)
	if(not db.user_exists(message.from_user.id)):
		#если юзера нет в базе добавляем его
		db.add_user(message.from_user.username,message.from_user.id,message.from_user.full_name)


#Хендлеры для создания хаты


class CreateHata(StatesGroup):
    name = State()
    description = State()
    data = State()
    city = State()
    photo = State()
    social_link = State()
@dp.message_handler(lambda message: message.text.startswith('Создать хату🏠'),state='*')
async def create_hata(message: types.Message):
	if message.from_user.username != None:
		if(not db.hata_exists(message.from_user.id)):
			await message.answer("Для того что бы создать хату нужно заполнить несколько пунктов\nДавайте начнём с названия, введите желаемое названия для вашего треп хауса😉")
			await CreateHata.name.set()
		elif(db.hata_exists(message.from_user.id)) :
			await message.answer('У тебя уже есть активная хата!')
	else:
		await message.answer('‼️У вас не заполнен username в телеграм!\n\nПожалуйста сделайте это для коректного функционирования бота\nДля этого зайдите в настройки -> Edit Profile(Изменить профиль) и жмякайте add username\n\nТам вводите желаемый никнейм и вуаля')
@dp.message_handler(state=CreateHata.name)
async def create_hata_name(message: types.Message, state: FSMContext):
	if len(message.text) < 35: 
		await state.update_data(hata_name=message.text)
		await message.reply(message.text + ' - прекрасное название\nТеперь нужно заполнить описание👇\nбез этого никак прости :9')
		await CreateHata.next()
	else:
		await message.answer(custom_answer.random_reapeat_list())
		#прерывание функции
		return
@dp.message_handler(state=CreateHata.description)
async def create_hata_description(message: types.Message, state: FSMContext):
	if len(message.text) < 250:
		await state.update_data(hata_description=message.text)

		button_to_day = KeyboardButton('Сегодня')
		button_tomorrow = KeyboardButton('Завтра')
		button_after_tomorrow = KeyboardButton('Послезавтра')

		all_btn_days = ReplyKeyboardMarkup(one_time_keyboard=True)
		all_btn_days.add(button_to_day,button_tomorrow,button_after_tomorrow)
		await message.reply('Ебнутое описание,предлагаю заполнить дату, когда пройдят твоя вечеринка с бассеином(или без:) и на этом эта мучительное заполнение закончится\nДля этого нажми на любую кнопку внизу',reply_markup=all_btn_days)
		await CreateHata.next()
	else:
		await message.answer(custom_answer.random_reapeat_list())
		#прерывание функции
		return
@dp.message_handler(state=CreateHata.data)
async def create_hata_data(message: types.Message, state: FSMContext):
	if message.text == 'Сегодня' or message.text == 'Завтра' or message.text == 'Послезавтра':
		if message.text == 'Сегодня':
			await state.update_data(hata_data=datetime.date.today())
		elif message.text == 'Завтра':
			await state.update_data(hata_data=datetime.date.today() + timedelta(days=1))
		elif message.text == 'Послезавтра':
			await state.update_data(hata_data=datetime.date.today() + timedelta(days=2))

		await message.reply('Прекрасно,осталось лишь понять где находится твоё чудное место\nУкажи город, где находится твой Вписка Хаус =)')
		await CreateHata.next()
	else:
		await message.answer(custom_answer.random_reapeat_list())
		#прерывание функции
		return
@dp.message_handler(state=CreateHata.city)
async def create_hata_city(message: types.Message, state: FSMContext):
	#проверка на длину строки города
	if len(message.text) < 35:
		#кнопки для меню 

		button_search = KeyboardButton('Все хаты🔍')
		button_create_hata = KeyboardButton('Создать хату🏠')
		button_delete_hata = KeyboardButton('Удалить хату❌')

		all_btn_menu = ReplyKeyboardMarkup(one_time_keyboard=True)

		user_name = message.from_user.username
		await state.update_data(hata_city=message.text.lower())
		user_data = await state.get_data()
		await message.answer('Анкета успешно создана!',reply_markup=all_btn_menu)
		#запрос на создания строки в бд
		db.create_hata(message.from_user.id,str(user_data['hata_description']),str(user_data['hata_name']),str(user_data['hata_data']),str(user_data['hata_city']),user_name,datetime.date.today())
		#конец state линии
		await state.finish()
	else:
		await message.answer(custom_answer.random_reapeat_list)
		#прерывание функции
		return

#Удаление хаты
@dp.message_handler(lambda message : message.text == 'Удалить хату❌',state='*')
async def delete_hata(message: types.Message):
	#кнопки для меню
	button_search = KeyboardButton('Найти хату🔍')
	button_create_hata = KeyboardButton('Создать хату🏠')
	button_delete_hata = KeyboardButton('Удалить хату❌')

	all_btn_menu = ReplyKeyboardMarkup(one_time_keyboard=True)

	if db.hata_exists(message.from_user.id):
		db.delete_hata(message.from_user.id)
		await message.answer('Ваша хата была удалена!',reply_markup=all_btn_menu  )
	else:
		await message.answer('У тебя и так её нет :(\n(хы-хы)')

#хендлеры для поиска хаты
class SearchHata(StatesGroup):
	city_for_search = State()
@dp.message_handler(lambda message : message.text == 'Найти хату🔍',state='*')
async def search_hata(message: types.Message):
	await message.answer('Для поиска хаты впишите город, где вы хотите трепить)')
	await SearchHata.city_for_search.set()
class ID_hata(StatesGroup):
	id = State()
@dp.message_handler(state=SearchHata.city_for_search)
async def create_hata_city(message: types.Message, state: FSMContext):
	#проверка на длину строки города
	if len(message.text) < 35:
		try:
			await state.update_data(search_hata_city=message.text.lower())
			user_data = await state.get_data()
			if bool(len(db.search_hata(user_data['search_hata_city'],'hata_id'))):
				all_hata_in_city_final = ''

				for i in range(0,db.count_hata(str(user_data['search_hata_city']))):
					all_hata_in_city_id = str(db.search_hata(str(user_data['search_hata_city']),'hata_id')[i][0])
					all_hata_in_city_name = str(db.search_hata(str(user_data['search_hata_city']),'name_hata')[i][0])
					all_hata_in_city_descp = str(db.search_hata(str(user_data['search_hata_city']),'description')[i][0])
					all_hata_in_city_data = str(db.search_hata(str(user_data['search_hata_city']),'data_fr_delete')[i][0])
					if all_hata_in_city_data == str(datetime.date.today()):
						all_hata_in_city_data = 'Сегодня'
					elif all_hata_in_city_data == str(datetime.date.today() + timedelta(days=1)):
						all_hata_in_city_data = 'Завтра'
					elif all_hata_in_city_data == str(datetime.date.today() + timedelta(days=2)):
						all_hata_in_city_data  = 'Послезавтра'
					all_hata_in_city_final = all_hata_in_city_final + 'Айдишник - ' + all_hata_in_city_id + '\nНазвание - ' + all_hata_in_city_name + '\nОписание - ' + all_hata_in_city_descp + '\nВремя проведения - ' + all_hata_in_city_data + '\n#-#-#-#-#-#-#-#-#-#-#-#\n'
				
				#кнопки
				button_funny_alert = KeyboardButton('Да,да написать прям тут☝️')

				all_btn = ReplyKeyboardMarkup()
				all_btn.add(button_funny_alert)					

				await message.answer('Для того что бы выбрать желаемую - впиши ID.\nВсе тусы в городе ' + str(user_data['search_hata_city']).title() + ':\n\n' + all_hata_in_city_final,reply_markup=all_btn)
				#конец state линии
				await state.finish()
				await ID_hata.id.set()
			else:
				await message.answer('В этом городе не тус!')
		except:
			await message.answer('В этом городе нету хат или ты допустил ошибку!')
	else:
		await message.answer(custom_answer.random_reapeat_list())
		#прерывание функции
		return
#Хедлер для фи
@dp.message_handler(state=ID_hata.id)
async def hata_search_id_send(message: types.Message, state: FSMContext):
	await state.update_data(hata_id_for_search=message.text)
	user_data = await state.get_data()
	try:
		if int(user_data['hata_id_for_search']) in range(1,99999):
			try:	
				search_id_request = db.search_hata_id(str(user_data['hata_id_for_search']))[0]
			except:
				search_id_request = 'нету('
			await message.answer('Надеюсь хорошо проведете время ;)\nСписывайтесь,договаривайтесь,ваше здоровье🍻\nЧего ты ждёшь - @' + str(search_id_request))
			await bot.send_message(db.search_hata_tg_id(str(user_data['hata_id_for_search']))[0],'Твоей хатой заинтеравлся пользователь @' + str(message.from_user.username))
			return 
			await state.finish()	
	except Exception as e:
		await message.answer(custom_answer.random_reapeat_list())
		print(e)
		return
#функция для удаление устаревших хат
async def hata_timer(wait_for):
	while True:
		await asyncio.sleep(wait_for)
		now = datetime.date.today()

		db.delete_hata_timer(str(now - timedelta(days=1)))
#хендлер для рофла)		
@dp.message_handler(lambda message : message.text == 'Да,да написать прям тут☝️',state='*')
async def funny_alert(message : types.Message):
	funny_list = ['Да не сюда тыкать, а написать в чат!😡','Ты чё совсем *#*#43*~* писать вверху','В чат пиши блин,буковками вверху!!!']
	await message.answer(random.choice(funny_list))

#хендлер который срабатывает при непредсказуемом запросе юзера
@dp.message_handler()
async def end(message : types.Message):
	await message.answer('Я не знаю, что с этим делать 😲\nЯ просто напомню, что есть команда /help =)',parse_mode=ParseMode.MARKDOWN)

#запуск полинга бота
dp.loop.create_task(hata_timer(600))	
executor.start_polling(dp, skip_updates=True)
