from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives import hashes
import json
from os import urandom
from cryptography.hazmat.primitives import hashes

class User:
	def __init__(self, username, password, salt=None): 
		self.username = username
		self.salt = salt if salt else urandom(16)
		self.password = self.crear_hash(password) if not salt else password
    
	@staticmethod
	def register(username, password): 
		user = User(username, password)
		user.save_to_file()
		return user
    
	def save_to_file(self):
		datos_usuario = {
			'username': self.username,
			'password': self.password,
			'salt': urlsafe_b64encode(self.salt).decode()
		}
		try:
			with open("users.json", "r") as f:
				datos = json.load(f)
		except FileNotFoundError:
			datos = []
   
		datos.append(datos_usuario)
  
		with open("users.json", "w") as f:
			json.dump(datos, f)

	def login(self, username, password):
		user = User.get_user(username)
		if user and user.verificar_contrasenia(password):
			print("Has iniciado sesión correctamente!")
			return True
		return False


	def crear_hash(self, text):
		contrasenia = PBKDF2HMAC(
			algorithm=hashes.SHA256(),
			length=32,
			salt=self.salt,
			iterations=100000,
			backend=default_backend()
		)
		return urlsafe_b64encode(contrasenia.derive(text.encode())).decode()

	def verificar_contrasenia(self, contrasenia):
		nuevo_hash = self.crear_hash(contrasenia)
		return self.password == nuevo_hash
    

	@staticmethod
	def get_user(username):
		try:
			with open("users.json", "r") as f:
				datos = json.load(f)
				for usuario in datos:
					if usuario['username'] == username:
						salt = urlsafe_b64decode(usuario['salt'].encode())
						user = User(usuario['username'], usuario['password'], salt)
						user.password = usuario['password']  
						return user
		except (FileNotFoundError, json.JSONDecodeError):
				return None
		return None