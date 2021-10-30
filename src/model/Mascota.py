from src.connection.EasyConnection import EasyConnection
from src.routes.HTTPStatus import BAD_REQUEST, CONFLICT, NOT_ACCEPTABLE, NOT_FOUND, OK, \
	RESOURCE_CREATED


class Mascota:
	def __init__(self):
		self.id_mascota = None
		self.nombre = None
		self.color = None
		self.sexo = None
		self.especie = None
		self.edad = None
		self.edad = None
		self.peso = None
		self.tamanio = None
		self.estado = None
		self.raza_aparente = None
		self.conexion = EasyConnection.build_from_static()

	def guardar(self) -> int:
		estado = BAD_REQUEST
		if self.nombre is not None:
			query = "CALL SPI_registrarMascota(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
			valores = [
				self.nombre,
				self.color,
				self.sexo,
				self.especie,
				self.edad,
				self.peso,
				self.tamanio,
				self.estado,
				self.raza_aparente
			]
			resultado = self.conexion.select(query, valores)
			if resultado:
				self.id_mascota = resultado[0]["_id_mascota"]
				estado = RESOURCE_CREATED
			else:
				estado = CONFLICT
		else:
			estado = NOT_ACCEPTABLE
		return estado

	def actualizar(self) -> int:
		estado = BAD_REQUEST
		if self.id_mascota is not None:
			query = "CALL SPA_actualizarMascota(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			valores = [
				self.id_mascota,
				self.nombre,
				self.color,
				self.sexo,
				self.especie,
				self.edad,
				self.peso,
				self.tamanio,
				self.estado,
				self.raza_aparente
			]
			estado = NOT_FOUND
			if self.conexion.send_query(query, valores):
				estado = OK
		return estado

	def cargar(self) -> bool:
		cargado = False
		if self.id_mascota is not None:
			query = "CALL SPS_obtenerMascota(%s)"
			valores = [self.id_mascota]
			resultado = self.conexion.select(query, valores)
			if resultado:
				cargado = self.cargar_de_json(resultado[0])
		return cargado

	def cargar_de_json(self, valores: dict) -> bool:
		cargado = False
		for atributo in self.__dict__:
			if atributo in valores:
				self.__setattr__(atributo, valores[atributo])
				cargado = True
		return cargado

	def eliminar(self) -> int:
		estado = BAD_REQUEST
		if self.id_mascota is not None:
			if self.cargar():
				query = "CALL SPE_eliminarMascota(%s)"
				valores = [self.id_mascota]
				if self.conexion.send_query(query, valores):
					estado = OK
				else:
					estado = NOT_ACCEPTABLE
			else:
				estado = NOT_FOUND
		return estado

	def jsonificar(self, valores_deseados=None) -> dict:
		diccionario = {}
		if valores_deseados is not None:
			for atributo in self.__dict__:
				if atributo in valores_deseados:
					diccionario[atributo] = self.__getattribute__(atributo)
		else:
			for atributo in self.__dict__:
				if atributo != "conexion":
					diccionario[atributo] = self.__getattribute__(atributo)
		return diccionario