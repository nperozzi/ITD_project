import sqlite3
from typing import Any, Dict, Optional

DB_PATH = 'sqlite.db'

class BackendDB:
	def __init__(self, db_path: str = DB_PATH):
		self.db_path = db_path
		
		with sqlite3.connect(self.db_path) as db_connection:
			db_connection.execute("PRAGMA foreign_keys = ON;")
			cursor = db_connection.cursor()
			cursor.execute("""
				  CREATE TABLE IF NOT EXISTS product (
				  id INTEGER PRIMARY KEY,
				  name TEXT NOT NULL,
				  price REAL NOT NULL
				  )
			""")
			
			cursor.execute("""
				CREATE TABLE IF NOT EXISTS tag (
					id INTEGER PRIMARY KEY,
					current_product_id INTEGER UNIQUE,
					battery_level INTEGER,
					FOREIGN KEY (current_product_id) REFERENCES product(id)
				)
			""")
			db_connection.commit()

			self.testing_records(DB_PATH)
			
			
	def set_tag(self, tag_id: int, current_product_id: Optional[int], battery_level: Optional[int]):
		with sqlite3.connect(self.db_path) as db_connection:
			cursor = db_connection.cursor()
			cursor.execute('''
				INSERT INTO tag (id, current_product_id, battery_level)
				VALUES (?, ?, ?)
				ON CONFLICT(id) DO UPDATE SET current_product_id=excluded.current_product_id, battery_level=excluded.battery_level
			''', (tag_id, current_product_id, battery_level))
			db_connection.commit()

	def get_tag(self, tag_id: int) -> Optional[Dict[str, Any]]:
		with sqlite3.connect(self.db_path) as db_connection:
			cursor = db_connection.cursor()
			cursor.execute('''
				SELECT id, current_product_id, battery_level FROM tag WHERE id = ?
			''', (tag_id,))
			result = cursor.fetchone()
			if result:
				return {
					'id': result[0],
					'current_product_id': result[1],
					'battery_level': result[2]
				}
			return None

	def set_product_price(self, product_id: int, price: float):
		with sqlite3.connect(self.db_path) as db_connection:
			cursor = db_connection.cursor()
			cursor.execute('''
				UPDATE product SET price = ? WHERE id = ?
			''', (price, product_id))
			db_connection.commit()

	def testing_records(self, db_path: str = DB_PATH):
		"""
		At initialization we create tag01 and product01 for testing purposes
		"""
		self.db_path = db_path
		
		with sqlite3.connect(self.db_path) as db_connection:
			cursor = db_connection.cursor()
			# Insert initial product if not exists
			cursor.execute("""
				INSERT OR IGNORE INTO product (id, name, price)
				VALUES (?, ?, ?)
			""", (1, 'bananas', 10))
			# Insert initial tag if not exists
			cursor.execute("""
				INSERT OR IGNORE INTO tag (id, current_product_id, battery_level)
				VALUES (?, ?, ?)
			""", (1, 1, None))
			db_connection.commit()

