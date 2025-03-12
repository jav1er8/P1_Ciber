from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hmac, hashes
from cryptography.hazmat.backends import default_backend
from os import urandom
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import json
import Contenedor

class Vault: 
	def __init__(self, user):
		self.user = user
		self.contenedores = {}
		self.nombre_fichero = f"{self.user.username}.dat"
		self.clave = self._derive_key(user.password.encode())
		self.cargar_datos()
  
	def _derive_key(self, password):
		kdf = PBKDF2HMAC(
			algorithm=hashes.SHA256(),
			length=32,
			salt=self.user.salt,
			iterations=100000,
			backend=default_backend()
		)
		return kdf.derive(password)

	def anadir_contenedor(self, nombre):
		if nombre in self.contenedores:
			print("Contenedor ya existente")
			return False

		contenedor = Contenedor(nombre)
		self.contenedores[nombre] = contenedor
		return True

	def eliminar_contenedor(self, nombre):
		if nombre in self.contenedores:
			del self.contenedores[nombre]
			return True

		print("Contenedor no existente")
		return False

	def anadir_secreto(self, nombre, secreto):
		if nombre in self.contenedores:
				self.contenedores[nombre].append(secreto)
				return True
		return False

	def eliminar_secreto(self, nombre, secreto):
		if nombre in self.contenedores:
				self.contenedores[nombre].remove(secreto)
				return True
		return False

	def encriptar_datos(self, datos):
		#Convertimos los datos a bytes si no lo están
		if isinstance(datos, str):
				datos = datos.encode('utf-8')
		
		iv = urandom(16)
		cifrado = Cipher(algorithms.AES(self.clave), modes.GCM(iv), backend=default_backend())
		cifrador = cifrado.encryptor()
		datos_cifrados = cifrador.update(datos) + cifrador.finalize()
		return datos_cifrados, cifrador.tag, iv
    
	def desencriptar_datos(self, datos_cifrados, clave, tag, iv):
		iv = datos_cifrados[:16]
		tag = datos_cifrados[16:32]
		datos = datos_cifrados[32:]
		descifrado = Cipher(algorithms.AES(clave), modes.GCM(iv, tag), backend=default_backend())
		descifrador = descifrado.decryptor()
		return descifrador.update(datos) + descifrador.finalize()
    
	def guardar_datos(self):
		#Convertimos los contenedores a un formato serializable
		datos_serializables = {}
		for nombre, contenedor in self.contenedores.items():
			datos_serializables[nombre] = {
				'nombre': contenedor.nombre,
				'secretos': contenedor.secretos
			}
		
		datos_json = json.dumps(datos_serializables)
		datos_cifrados, tag, iv = self.encriptar_datos(datos_json)
		
		#Genero hmac para asegurar la integridad de los datos
		h = hmac.HMAC(self.clave, hashes.SHA256(), backend=default_backend())
		h.update(iv + tag + datos_cifrados)
		hmac_creado = h.finalize()

		#Guardamos todo en el archivo
		with open(self.nombre_fichero, 'wb') as f:
			f.write(iv + tag + hmac_creado + datos_cifrados)
    

	def cargar_datos(self):
		try:
			with open(self.nombre_fichero, 'rb') as f:
				datos = f.read()
				if len(datos) < 32:  #IV(16) + TAG(16) mínimo
						return
				
				iv = datos[:16]
				tag = datos[16:32]
				hmac_creado = datos[32:64]
				datos_cifrados = datos[64:]

				hmac_obtenido = hmac.HMAC(self.clave, hashes.SHA256(), backend=default_backend())
				hmac_obtenido.update(iv + tag + datos_cifrados)

				try:
					hmac_obtenido.verify(hmac)
					print("Integridad de los datos verificada")
				except:
					print("Error en la verificación de la integridad de los datos")
					return
				
				datos_json = self.desencriptar_datos(datos_cifrados, tag, iv).decode()
				datos_deserializados = json.loads(datos_json)
				
				#recreamos los contenedores
				for nombre, datos_contenedor in datos_deserializados.items():
					contenedor = Contenedor(nombre)
					contenedor.secretos = datos_contenedor['secretos']
					self.contenedores[nombre] = contenedor
								
		except (FileNotFoundError, json.JSONDecodeError):
			#Si el archivo no existe o está corrupto, empezamos con un vault vacío
			pass

        
	def obtener_secretos(self, nombre):
		if nombre in self.contenedores:
			return self.contenedores[nombre].secretos
		return None