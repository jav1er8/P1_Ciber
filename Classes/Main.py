from SecureBox import SecureBox

class Main:
    def __init__(self):
        self.sb = SecureBox()
        self.menu_principal()

    def menu_principal(self):
        while True:
            print("\nBienvenido a SecureBox!")
            print("1. Iniciar sesión")
            print("2. Registrarse")
            print("3. Salir")
            opcion = input("Selecciona una opción: ")

            if opcion == "1":
                self.login()
            elif opcion == "2":
                self.registrar()
            elif opcion == "3":
                print("Hasta la próxima!")
                exit()
            else:
                print("Opción no válida. Inténtalo de nuevo.")

    def login(self):
        username = input("Nombre de usuario: ")
        password = input("Contraseña: ")
        if self.sb.login(username, password):
            self.menu_usuario()
        else:
            print("Usuario o contraseña incorrectos.")

    def registrar(self):
        username = input("Elige un nombre de usuario: ")
        password = input("Elige una contraseña: ")
        if self.sb.registrar_usuario(username, password):
            print("Usuario registrado correctamente!")
        else:
            print("Error en el registro. Puede que el usuario ya exista.")

    def menu_usuario(self):
        while True:
            print("\nMenú de usuario:")
            print("1. Autenticarse con Google Drive")
            print("2. Listar archivos en Google Drive")
            print("3. Subir archivo a Google Drive")
            print("4. Descargar archivo desde Google Drive")
            print("5. Crear contenedor")
            print("6. Eliminar contenedor")
            print("7. Ver contenedores")
            print("8. Añadir secreto a un contenedor")
            print("9. Eliminar secreto de un contenedor")
            print("10. Ver secretos de un contenedor")
            print("11. Cerrar sesión")
            opcion = input("Selecciona una opción: ")

            if opcion == "1":
                if self.sb.autenticar_google_drive():
                    print("Autenticación exitosa!")
                else:
                    print("Error en la autenticación.")
            elif opcion == "2":
                self.sb.listar_vaults()
            elif opcion == "3":
                archivo = input("Ruta del archivo a subir: ")
                if self.sb.subir_archivo_drive(archivo):
                    print("Archivo subido correctamente!")
                else:
                    print("Error al subir el archivo.")
            elif opcion == "4":
                archivo_id = input("ID del archivo a descargar: ")
                destino = input("Ruta de destino: ")
                if self.sb.descargar_archivo_drive(archivo_id, destino):
                    print("Archivo descargado correctamente!")
                else:
                    print("Error al descargar el archivo.")
            elif opcion == "5":
                nombre = input("Nombre del contenedor: ")
                if self.sb.crear_contenedor(nombre):
                    print("Contenedor creado correctamente!")
                else:
                    print("Error al crear el contenedor.")
            elif opcion == "6":
                nombre = input("Nombre del contenedor a eliminar: ")
                if self.sb.eliminar_contenedor(nombre):
                    print("Contenedor eliminado correctamente!")
                else:
                    print("Error al eliminar el contenedor.")
            elif opcion == "7":
                self.sb.ver_contenedor()
            elif opcion == "8":
                nombre = input("Nombre del contenedor: ")
                secreto = input("Introduce el secreto: ")
                if self.sb.anadir_secreto(nombre, secreto):
                    print("Secreto añadido correctamente!")
                else:
                    print("Error al añadir el secreto.")
            elif opcion == "9":
                nombre = input("Nombre del contenedor: ")
                secreto = input("Introduce el secreto a eliminar: ")
                if self.sb.eliminar_secreto(nombre, secreto):
                    print("Secreto eliminado correctamente!")
                else:
                    print("Error al eliminar el secreto.")
            elif opcion == "10":
                nombre = input("Nombre del contenedor: ")
                self.sb.ver_secretos(nombre)
            elif opcion == "11":
                print("Cerrando sesión...")
                break
            else:
                print("Opción no válida. Inténtalo de nuevo.")

# Main
if __name__ == "__main__":
    Main()
