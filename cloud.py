import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

class CloudIntegration:
    def __init__(self, vault):
        self.vault = vault
        self.drive = None
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.TOKEN_PATH = 'token.pickle'
        self.CREDENTIALS_PATH = 'credentials.json'
        
    def authenticate(self):
        """Autentica la aplicación con Google Drive."""
        creds = None
        
        #Intentar cargar credenciales desde archivo token
        if os.path.exists(self.TOKEN_PATH):
            with open(self.TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        
        #Si no hay credenciales válidas, solicitarlas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_PATH, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            #Guardar las credenciales para la próxima ejecución
            with open(self.TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
                
        #Inicializar el servicio de Drive
        gauth = GoogleAuth()
        gauth.credentials = creds
        self.drive = GoogleDrive(gauth)
        
        print("Autenticado correctamente con Google Drive")
        return True
        
    def backup_vault(self):
        """Sube el archivo vault a Google Drive."""
        if not self.drive:
            if not self.authenticate():
                print("Error en la autenticación con Google Drive")
                return False
                
        #Verificar si el archivo local existe
        if not os.path.exists(self.vault.nombre_fichero):
            print(f"El archivo {self.vault.nombre_fichero} no existe localmente")
            return False
            
        #Buscar si ya existe un backup previo
        file_list = self.drive.ListFile({'q': f"title='{self.vault.nombre_fichero}' and trashed=false"}).GetList()
        
        if file_list:
            #Actualizar el archivo existente
            drive_file = file_list[0]
            drive_file.SetContentFile(self.vault.nombre_fichero)
            drive_file.Upload()
            print(f"Backup actualizado en Google Drive: {drive_file['title']}")
        else:
            #Crear un nuevo archivo
            drive_file = self.drive.CreateFile({'title': self.vault.nombre_fichero})
            drive_file.SetContentFile(self.vault.nombre_fichero)
            drive_file.Upload()
            print(f"Backup creado en Google Drive: {drive_file['title']}")
            
        return True
        
    def restore_vault(self):
        """Restaura el archivo vault desde Google Drive."""
        if not self.drive:
            if not self.authenticate():
                print("Error en la autenticación con Google Drive")
                return False
                
        #Buscar el archivo en Drive
        file_list = self.drive.ListFile({'q': f"title='{self.vault.nombre_fichero}' and trashed=false"}).GetList()
        
        if not file_list:
            print(f"No se encontró ningún backup para {self.vault.nombre_fichero} en Google Drive")
            return False
            
        #Descargar el archivo
        drive_file = file_list[0]
        drive_file.GetContentFile(self.vault.nombre_fichero)
        print(f"Vault restaurado desde Google Drive: {drive_file['title']}")
        
        #Recargar los datos
        self.vault.cargar_datos()
        return True
    
    def list_backups(self):
        """Lista los backups disponibles en Google Drive."""
        if not self.drive:
            if not self.authenticate():
                print("Error en la autenticación con Google Drive")
                return []
                
        #Buscar archivos .dat en Drive
        file_list = self.drive.ListFile({'q': "title contains '.dat' and trashed=false"}).GetList()
        
        if not file_list:
            print("No se encontraron backups en Google Drive")
            return []
            
        print("Backups disponibles en Google Drive:")
        for i, file in enumerate(file_list):
            print(f"{i+1}. {file['title']} (Modificado: {file['modifiedDate']})")
            
        return file_list

#Integración con la clase SecureBox

def integrate_cloud_to_securebox(SecureBox):
    """Modifica la clase SecureBox para añadir funcionalidad de nube."""
    
    #Inicializar la integración con la nube
    old_init = SecureBox.__init__
    
    def new_init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        self.cloud = None
        
    SecureBox.__init__ = new_init
    
    #Añadir método para inicializar la nube
    def init_cloud(self):
        if self.vault:
            self.cloud = CloudIntegration(self.vault)
            return True
        print("Inicie sesión primero para configurar la nube")
        return False
    
    SecureBox.init_cloud = init_cloud
    
    #Añadir método para hacer backup
    def backup_to_cloud(self):
        if not self.cloud:
            if not self.init_cloud():
                return False
        return self.cloud.backup_vault()
    
    SecureBox.backup_to_cloud = backup_to_cloud
    
    #Añadir método para restaurar
    def restore_from_cloud(self):
        if not self.cloud:
            if not self.init_cloud():
                return False
        return self.cloud.restore_vault()
    
    SecureBox.restore_from_cloud = restore_from_cloud
    
    #Añadir método para listar backups
    def list_cloud_backups(self):
        if not self.cloud:
            if not self.init_cloud():
                return []
        return self.cloud.list_backups()
    
    SecureBox.list_cloud_backups = list_cloud_backups
    
    return SecureBox



#Aplicar la integración con la nube
SecureBox = integrate_cloud_to_securebox(SecureBox)

#En el menú principal se pueden añadir opciones para la nube:
if opcion == "8":
    print("Creando backup en la nube...")
    if sb.backup_to_cloud():
        print("Backup creado correctamente!")
    else:
        print("Error al crear el backup")

if opcion == "9":
    print("Restaurando desde la nube...")
    if sb.restore_from_cloud():
        print("Restauración completada correctamente!")
    else:
        print("Error en la restauración")

if opcion == "10":
    print("Listando backups en la nube...")
    sb.list_cloud_backups()





"""
Pasos:


pip install pydrive2 google-auth google-auth-oauthlib google-auth-httplib2

Ve a Google Cloud Console
Crea un nuevo proyecto
Activa la API de Google Drive
Crea credenciales OAuth 2.0 para tu aplicación
Descarga el archivo JSON de credenciales y guárdalo como credentials.json en la misma carpeta que tu script





"""