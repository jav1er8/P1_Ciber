import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from User import User
from Vault import Vault
from Contenedor import Contenedor

# Ruta a los archivos desde la carpeta 'Classes'
credentials_path = os.path.join(os.path.dirname(__file__), '../Conf', 'credentials.json')
token_path = os.path.join(os.path.dirname(__file__), '../Conf', 'token.json')

class SecureBox:
    def __init__(self): 
        self.users = {}  # Usuarios registrados
        self.usuario_actual = None  # Usuario actual
        self.vault = None  # Vault con los contenedores del usuario
        self.credentials = None
        self.drive_service = None

    def autenticar_google_drive(self):
        """ Autentica con Google Drive usando token.json si existe """
        SCOPES = ['https://www.googleapis.com/auth/drive']

        # Si ya existe el token.json, cargamos las credenciales
        if os.path.exists(token_path):
            self.credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
        else:
            # Si no existe el archivo token.json, hacemos el flujo de autenticación
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            self.credentials = flow.run_local_server(port=0)
            # Guardamos las credenciales en token.json para la próxima vez
            with open(token_path, 'w') as token:
                token.write(self.credentials.to_json())

        # Verificamos si las credenciales son válidas
        if self.credentials and self.credentials.valid:
            self.drive_service = build("drive", "v3", credentials=self.credentials)
            return True
        else:
            print("Error al autenticar con Google Drive.")
            return False

    def listar_archivos_drive(self):
        """ Lista los archivos en Google Drive """
        if not self.drive_service:
            print("Error: No autenticado con Google Drive")
            return []

        try:
            results = self.drive_service.files().list(fields="files(id, name)").execute()
            archivos = results.get("files", [])
            
            if not archivos:
                print("No se encontraron archivos en Drive.")
            else:
                print("Archivos en Drive:")
                for archivo in archivos:
                    print(f"- {archivo['name']} (ID: {archivo['id']})")
            return archivos
        except HttpError as error:
            print(f"Error al listar archivos: {error}")
            return []

    def subir_archivo_a_drive(self, archivo_path):
        """ Sube un archivo a Google Drive """
        if not self.drive_service:
            print("Error: No autenticado con Google Drive")
            return None

        try:
            from googleapiclient.http import MediaFileUpload  # Necesario para subir archivos
            file_metadata = {'name': os.path.basename(archivo_path)}
            media = MediaFileUpload(archivo_path, resumable=True)
            archivo = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"Archivo subido con ID: {archivo['id']}")
            return archivo['id']
        except HttpError as error:
            print(f"Error al subir archivo: {error}")
            return None

    def descargar_archivo_desde_drive(self, file_id, destino_path):
        """ Descarga un archivo desde Google Drive """
        if not self.drive_service:
            print("Error: No autenticado con Google Drive")
            return False

        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            with open(destino_path, "wb") as archivo:
                archivo.write(request.execute())
            print(f"Archivo descargado en: {destino_path}")
            return True
        except HttpError as error:
            print(f"Error al descargar archivo: {error}")
            return False

    def listar_vaults(self):
        """ Lista los archivos en Google Drive que sean vaults """
        archivos = self.listar_archivos_drive()
        vaults = [archivo for archivo in archivos if '.vault' in archivo['name']]

        if not vaults:
            print("No se encontraron vaults.")
        else:
            print("Vaults disponibles:")
            for vault in vaults:
                print(f"- {vault['name']} (ID: {vault['id']})")

        return vaults

    def registrar_usuario(self, username, password):
        if username in self.users:
            print("Usuario ya registrado")
            return False
        
        user = User.register(username, password)
        self.users[username] = user
        return True
    
    def login(self, username, password):
        user = User.get_user(username)
        if user and user.verificar_contrasenia(password):
            self.usuario_actual = user
            self.vault = Vault(user)
            print("Has iniciado sesión correctamente!")
            return True
        return False

    def crear_contenedor(self, nombre):
        if nombre in self.vault.contenedores:
            print("Contenedor ya existente")
            return False
        
        contenedor = Contenedor(nombre)
        self.vault.contenedores[nombre] = contenedor
        self.vault.guardar_datos()
        return True

    def eliminar_contenedor(self, nombre):
        if nombre in self.vault.contenedores:
            del self.vault.contenedores[nombre]
            self.vault.guardar_datos()
            return True
        return False

    def ver_contenedor(self):
        if self.vault:
            if not self.vault.contenedores:
                print("No hay contenedores")
                return
            for contenedor in self.vault.contenedores:
                print(contenedor)
        return None

    def anadir_secreto(self, nombre, secreto):
        if nombre in self.vault.contenedores:
            self.vault.contenedores[nombre].append(secreto)
            self.vault.guardar_datos()
            return True
        return False

    def eliminar_secreto(self, nombre, secreto):
        if nombre in self.vault.contenedores:
            result = self.vault.contenedores[nombre].remove(secreto)
            if result:
                self.vault.guardar_datos()
            return result
        return False

    def ver_secretos(self, nombre):
        if self.vault:
            secretos = self.vault.obtener_secretos(nombre)
            if secretos:
                print("Secretos en el contenedor:")
                for secreto in secretos:
                    print(secreto)
            else:
                print("No hay secretos en el contenedor")
        return None
