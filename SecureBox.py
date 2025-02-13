from Crypto.Hash import SHA256
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives import hashes
import sqlite3
import json
import pdb
from os import urandom

class User:
    def __init__(self, username, password, salt=None): 
        self.username = username
        self.salt = urandom(16)
        self.password = self.crear_hash(password)
    

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
        if self.username == username and self.password==self.crear_hash(password):
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
        return self.password == self.crear_hash(contrasenia)
    
    @staticmethod
    def get_user(username):
        try:
            with open("users.json", "r") as f:
                datos = json.load(f)
                for usuario in datos:
                    if usuario['username'] == username:
                        return User(usuario['username'], usuario['password'], urlsafe_b64decode(usuario['salt'].encode()))
        except FileNotFoundError:
            return None
        return None



class Vault:
    def __init__(self, user):
        self.user = user
        self.contenedores = {}
    
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
    
    def obtener_secretos(self, nombre):
        if nombre in self.contenedores:
            return self.contenedores[nombre]
        return None
    
    def encriptar_datos(self, datos, clave):
        #Usaremos el AES como estudiamos en criptografía
        iv = urandom(16)
        cifrado = Cipher(algorithms.AES(clave), modes.GCM(iv), backend=default_backend())
        cifrador = cifrado.encryptor()
        datos_cifrados = cifrador.update(datos) + cifrador.finalize()
        return datos_cifrados + cifrador.tag + iv
    
    def desencriptar_datos(self, datos_cifrados, clave, tag, iv):
        iv = datos_cifrados[:16]
        tag = datos_cifrados[16:32]
        datos = datos_cifrados[32:]
        descifrado = Cipher(algorithms.AES(clave), modes.GCM(iv, tag), backend=default_backend())
        descifrador = descifrado.decryptor()
        return descifrador.update(datos) + descifrador.finalize()
    
    def guardar_datos(self, fichero, clave):
        datos = json.dumps(self.contenedores)
        encriptados = self.encriptar_datos(datos, clave)
        with open(fichero, 'wb') as f:
            f.write(encriptados)
    
    def cargar_datos(self, fichero, clave):
        with open(fichero, 'rb') as f:
            datos = f.read()
        datos_desencriptados = self.desencriptar_datos(datos, clave)
        self.contenedores = json.loads(datos_desencriptados.decode())
        


class SecureBox:
    def __init__(self): 
        self.users = {}
    
    def registrar_usuario(self, username, password):
        if username in self.users:
            print("Usuario ya registrado")
            return False

        user = User.register(username, password)
        self.users[username] = user
        return True
    
    def login(self, username, password):
        if username in self.users:
            return self.users[username].login(username, password)
        else:
            print("Usuario no registrado")
            return False
        
    def cargar_usuario(self, username):
        usuarios = {}
        try:
            with open("users.json", "r") as f:
                datos = json.load(f)
                for usuario in datos:
                    usuarios[usuario['username']] = User(usuario['username'], usuario['password'], urlsafe_b64decode(usuario['salt'].encode()))
        except FileNotFoundError:
            return None
        return usuarios.get(username, None)



#Clase que inicia el programa, recoge los datos de usuario y los guarda en un objeto de tipo User
class Launcher:
    def __init__(self, username, password): 
        self.user = User.register(username, password)
        self.numMaxTries = 5
        self.actualTries = 0
        
    def login_user(self, username, password): 
        if (username == None or password == None):
            print("Usuario o contraseña nulos")

        if self.actualTries == self.numMaxTries:
            print("Número de intentos superado, ha sido BANEADO")
            return False

        self.actualTries += 1
        return self.user.login(username, password)

    def register_user(self, username, password): 
        if (username == None or password == None):
            print("Usuario o contraseña nulos")
        
        return self.user.register(username, password)
    

if __name__ == "__main__":

    sb = SecureBox()

    while True:
        print("Bienvenido a tu almacén de contraseñas de confianza!")
        print("¿Qué deseas hacer?")
        print("1. LogIn")
        print("2. Register")
        print("3. Exit")
        print("Introduce el número de la opción deseada:")
        option = input()
        #pdb.set_trace()

        if option == "1":
            print("Introduce tu nombre de usuario:")
            username = input()
            print("Introduce tu contraseña:")
            password = input()
            launcher = Launcher(username, password)
            if launcher.login_user(username, password):
                print("Has iniciado sesión correctamente!")

            else:
                print("Usuario o contraseña incorrectos")
            break

        if option == "2":
            print("Introduce tu nombre de usuario:")
            username = input()
            print("Introduce tu contraseña:")
            password = input()
            launcher = Launcher(username, password)
            if launcher.register_user(username, password):
                print("Usuario registrado correctamente!")
            else:
                print("Error en el registro")
            break

        if option == "3":
            print("Hasta la próxima!")
            exit()

        else:
            print("Opción no válida, por favor, introduce un número del 1 al 3")




#Cambio realizados

#Cambio SHA256 por PBKDF2HMAC ya que es resistente a ataques de fuerza bruta 
#Uso sqlite3 para almacenar los datos de los usuarios
#Uso libreria cryptography para usar AES en modo GCM (lo dimos en cripto)
#Añado @staticmethod a la función register, ya que no necesita de una instancia para ser llamada