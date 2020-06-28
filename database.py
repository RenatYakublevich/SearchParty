import sqlite3

class dbworker:
	def __init__(self,database_file):
		self.connection = sqlite3.connect(database_file)
		self.cursor = self.connection.cursor()
	def subscriber_exists(self, user_id):
		#Проверка есть ли юзер в бд
		with self.connection:	
			result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
			return bool(len(result))	
	def add_subscriber(self, user_id, status = False):
		#Добавляем нового юзера
		with self.connection:
			return self.cursor.execute("INSERT INTO `users` (`user_id`, `status`) VALUES(?,?)", (user_id,status))
	def create_hata(self,user_id,description,name_hata,data_fr_delete,city,telegram_username,data_creating):
		#Создаём хату
		with self.connection:
			return self.cursor.execute("INSERT INTO `hata_list` (`telegram_id`,`description`,`name_hata`,`data_fr_delete`,`city`,`telegram_username`,`data_creating`) VALUES(?,?,?,?,?,?,?)", (user_id,description,name_hata,data_fr_delete,city,telegram_username,data_creating))
	def hata_exists(self,user_id):
		#Проверка есть ли хата в бд
		with self.connection:	
			result = self.cursor.execute('SELECT * FROM `hata_list` WHERE `telegram_id` = ?', (user_id,)).fetchall()
			return bool(len(result))
	def delete_hata(self,user_id):
		#Удаление хаты
		with self.connection:
			return self.cursor.execute('DELETE FROM `hata_list` WHERE `telegram_id` = ?',(user_id,))
	def search_hata(self,city,method):
		#Поиск хат по городу
		with self.connection:
			return self.cursor.execute('SELECT ' + method + ' FROM `hata_list` WHERE `city` = ?',(city,)).fetchall()
	def search_hata_id(self,id):
		#Поиск username по id
		with self.connection:
			return self.cursor.execute('SELECT `telegram_username` FROM `hata_list` WHERE `hata_id` = ?',(id)).fetchone()
	def count_hata(self,city):
		#Количество хат по городу
		with self.connection:
			result = self.cursor.execute('SELECT * FROM `hata_list` WHERE  `city` = ?',(city,)).fetchall()
			return len(result)
	def close(self):
		#Закрываем соединение с БД
		self.connection.close()		
	def delete_hata_timer(self,data_fr_delete):
		with self.connection:
			return self.cursor.execute("DELETE FROM `hata_list` WHERE `data_fr_delete` = ?",(data_fr_delete))
