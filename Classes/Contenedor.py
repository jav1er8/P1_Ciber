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