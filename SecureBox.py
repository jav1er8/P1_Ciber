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
        self.salt = salt if salt else urandom(16)
        self.password = self.crear_hash(password) if salt else password
    
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


class Contenedor:
    def __init__(self, nombre):
        self.nombre = nombre
        self.secretos = []
    
    def append(self, secreto):
        self.secretos.append(secreto)
    
    def remove(self, secreto):
        if secreto in self.secretos:
            self.secretos.remove(secreto)
            return True
    
    def __str__(self):
        return f"Contendor: {self.nombre}, Secretos: {self.secretos}"


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
        contenedores = json.loads(datos_desencriptados.decode())
        for nombre, secretos in contenedores.items():
            self.contenedores[nombre] = Contenedor(nombre)
            self.contenedores[nombre].secretos = secretos
        
    def obtener_secretos(self, nombre):
        if nombre in self.contenedores:
            return self.contenedores[nombre].secretos
        return None


class SecureBox:
    def __init__(self): 
        self.users = {}
        self.usuario_actual = None
        self.vault = None
    
    def registrar_usuario(self, username, password):
        if username in self.users:
            print("Usuario ya registrado")
            return False

        user = User.register(username, password)
        self.users[username] = user
        return True
    
    #Función que comprueba si un usuario ya está registrado, se usa en el login
    def existe_usuario(self, username):
        return username in self.users
    
    def login(self, username, password):
        user = User.get_user(username)
        if user and user.verificar_contrasenia(password):
            self.usuario_actual = user
            self.vault = Vault(user)
            print("Has iniciado sesión correctamente!")
            return True
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
    
    def crear_contenedor(self, nombre):
        if self.vault:
            return self.vault.anadir_contenedor(nombre)
        return False
    
    def eliminar_contenedor(self, nombre):
        if self.vault:
            return self.vault.eliminar_contenedor(nombre)
        return False
    
    def ver_contenedor(self):
        if self.vault:
            if not self.vault.contenedores:
                print("No hay contenedores")
                return
            else:
                for contenedor in self.vault.contenedores:
                    print(contenedor)
        return None
    
    def anadir_secreto(self, nombre, secreto):
        if self.vault:
            return self.vault.anadir_secreto(nombre, secreto)
        return False
    
    def eliminar_secreto(self, nombre, secreto):
        if self.vault:
            return self.vault.eliminar_secreto(nombre, secreto)
        return False
    
    def ver_secretos(self, nombre):
        if self.vault:
            secretos = self.vault.obtener_secretos(nombre)
            if secretos:
                if len(secretos) == 0:
                    print("No hay secretos en el contenedor")
                else:
                    for secreto in secretos:
                        print(secreto)
                return
            print("No hay secretos en el contenedor")
        return None
    




#Clase que inicia el programa, recoge los datos de usuario y los guarda en un objeto de tipo User
class Launcher:
    def __init__(self, username, password): 
        self.user = User.register(username, password)
        self.numMaxTries = 5
        self.actualTries = 0
        
    def login_user(self, username, password): 
        if (username is None or password is None):
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

        if option == "1":
            print("Introduce tu nombre de usuario:")
            username = input()
            print("Introduce tu contraseña:")
            password = input()
            if sb.login(username, password):
                while True:
                    print("\n¿Qué deseas hacer?")
                    print("1. Crear contenedor")
                    print("2. Eliminar contenedor")
                    print("3. Ver contenedores")
                    print("4. Añadir secreto a un contenedor")
                    print("5. Eliminar secreto de un contenedor")
                    print("6. Ver secretos de un contenedor")
                    print("7. Cerrar sesión")
                    print("Introduce el número de la opción deseada:")
                    opcion = input()

                    if opcion == "1":
                        print("Introduce el nombre del contenedor:")
                        nombre = input()
                        if sb.crear_contenedor(nombre):
                            print("Contenedor creado correctamente!")
                        else:
                            print("Error al crear el contenedor")
                        

                    if opcion == "2":
                        print("Introduce el nombre del contenedor:")
                        nombre = input()
                        if sb.eliminar_contenedor(nombre):
                            print("Contenedor eliminado correctamente!")
                        else:
                            print("Error al eliminar el contenedor")
                        

                    if opcion == "3":
                        sb.ver_contenedor()
                        

                    if opcion == "4":
                        print("Introduce el nombre del contenedor:")
                        nombre = input()
                        print("Introduce el secreto:")
                        secreto = input()
                        if sb.anadir_secreto(nombre, secreto):
                            print("Secreto añadido correctamente!")
                        else:
                            print("Error al añadir el secreto")
                        

                    if opcion == "5":
                        print("Introduce el nombre del contenedor:")
                        nombre = input()
                        print("Introduce el secreto:")
                        secreto = input()
                        if sb.eliminar_secreto(nombre, secreto):
                            print("Secreto eliminado correctamente!")
                        else:
                            print("Error al eliminar el secreto")
                        

                    if opcion == "6":
                        print("Introduce el nombre del contenedor:")
                        nombre = input()
                        sb.ver_secretos(nombre)
                        

                    if opcion == "7":
                        print("Cerrando sesión...")
                        break


            else:
                print("Usuario o contraseña incorrectos")
            break

        if option == "2":
            print("Introduce tu nombre de usuario:")
            username = input()
            print("Introduce tu contraseña:")
            password = input()
            if sb.registrar_usuario(username, password):
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