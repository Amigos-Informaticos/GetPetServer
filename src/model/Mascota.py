from src.connection.EasyConnection import EasyConnection
from src.connection.EasyFTP import EasyFTP
from src.routes.HTTPStatus import BAD_REQUEST, CONFLICT, FILE_UPLOADED, INTERNAL_SERVER_ERROR, \
	NOT_ACCEPTABLE, \
	NOT_FOUND, NO_CONTENT, OK, \
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
		self.esterilizada = None
		self.desparacitada = None
		self.discapacitada = None
		self.descripcion = None
		self.registrador = 0
		self.conexion = EasyConnection.build_from_static()

	def guardar(self) -> int:
		estado = BAD_REQUEST
		if self.nombre is not None:
			query = "CALL SPI_registrarMascota(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			valores = [
				self.nombre,
				self.color,
				self.sexo,
				self.especie,
				self.edad,
				self.peso,
				self.tamanio,
				self.estado,
				self.raza_aparente,
				self.esterilizada,
				self.desparacitada,
				self.discapacitada,
				self.descripcion,
				self.registrador
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
			query = "CALL SPA_actualizarMascota(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
				self.raza_aparente,
				self.esterilizada,
				self.desparacitada,
				self.discapacitada,
				self.descripcion
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
			diccionario["imagenes"] = self.obtener_imagenes()
		return diccionario

	@staticmethod
	def buscar(nombre: str, especie: str, pagina: int) -> list:
		mascotas = []
		query = "CALL SPS_buscarMascotas(%s, %s, %s)"
		valores = [nombre, especie, pagina]
		conexion = EasyConnection.build_from_static()
		resultados = conexion.select(query, valores)
		if resultados:
			for fila in resultados:
				nueva_mascota = Mascota()
				nueva_mascota.cargar_de_json(fila)
				mascotas.append(nueva_mascota.jsonificar())
		return mascotas

	def guardar_imagen(self, file_obj) -> int:
		respuesta = NOT_FOUND
		if self.id_mascota is not None:
			query = "CALL SPI_subirImagenMascota(%s)"
			valores = [self.id_mascota]
			resultados = self.conexion.select(query, valores)
			respuesta = INTERNAL_SERVER_ERROR
			if resultados:
				path = f"m_{self.id_mascota}_{resultados[0]['conteo_imagenes']}.png"
				ftp = EasyFTP.build_from_static()
				ftp.connect()
				ftp.set_dir("pet_me_images")
				if ftp.upload_binary(file_obj, path, False):
					respuesta = FILE_UPLOADED
				ftp.close()
		return respuesta

	def obtener_imagen(self, id_imagen) -> tuple:
		respuesta = (NOT_FOUND, None)
		if self.id_mascota is not None:
			respuesta = (NO_CONTENT, None)
			query = "SELECT COUNT(*) AS TOTAL FROM ImagenMascota " \
			        "WHERE id_mascota = %s AND contador = %s"
			valores = [self.id_mascota, id_imagen]
			resultado = self.conexion.select(query, valores)
			if resultado[0]["TOTAL"] > 0:
				path = f"m_{self.id_mascota}_{id_imagen}.png"
				ftp = EasyFTP.build_from_static()
				ftp.connect()
				ftp.set_dir("pet_me_images")
				downloaded_file = ftp.download_binary(path)
				ftp.close()
				respuesta = (OK, downloaded_file)
		return respuesta

	def obtener_imagenes(self) -> list:
		imagenes = []
		if self.id_mascota is not None:
			query = "SELECT url FROM ImagenMascota WHERE id_mascota = %s"
			valores = [self.id_mascota]
			resultados = self.conexion.select(query, valores)
			for fila in resultados:
				imagenes.append(fila["url"])
		return imagenes

	def eliminar_imagen(self, id_imagen) -> int:
		respuesta = NOT_FOUND
		if self.id_mascota is not None:
			query = "DELETE FROM ImagenMascota WHERE id_mascota = %s AND contador = %s"
			valores = [self.id_mascota, id_imagen]
			respuesta = NO_CONTENT
			if self.conexion.send_query(query, valores):
				respuesta = OK
		return respuesta
