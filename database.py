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
	def close(self):
		#Закрываем соединение с БД
		self.connection.close()
	def create_hata(self,user_id,description,name_hata,data,city):
		with self.connection:
			return self.cursor.execute("INSERT INTO `hata_list` (`telegram_id`,`description`,`name_hata`,`data`,`city`) VALUES(?,?,?,?,?)", (user_id,description,name_hata,data,city))
	def hata_exists(self,user_id):
		#Проверка есть ли хата в бд
		with self.connection:	
			result = self.cursor.execute('SELECT * FROM `hata_list` WHERE `telegram_id` = ?', (user_id,)).fetchall()
			return bool(len(result))
	def delete_hata(self,user_id):
		#Удаление хаты
		with self.connection:
			return self.cursor.execute('DELETE FROM `hata_list` WHERE `telegram_id` = ?',(user_id,))