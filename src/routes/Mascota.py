import io
import json

from flask import Blueprint, Response, request, send_file

from src.model.Adoptante import Adoptante
from src.model.Mascota import Mascota
from src.routes.Auth import Auth
from src.routes.HTTPStatus import NOT_ACCEPTABLE, NOT_FOUND, NO_CONTENT, OK, RESOURCE_CREATED

rutas_mascota = Blueprint("rutas_mascota", __name__)


@rutas_mascota.post("/mascotas")
@Auth.requires_token
def registrar_mascota():
	respuesta = Response(status=NOT_ACCEPTABLE)
	if "nombre" in request.json:
		token = request.headers.get("Token")
		email = Auth.decode_token(token)["email"]

		adoptante = Adoptante()
		adoptante.email = email
		adoptante.cargar_adoptante()
		vals = request.json

		vals["registrador"] = adoptante.id_adoptante
		mascota = Mascota()
		mascota.cargar_de_json(vals)
		estado = mascota.guardar()
		respuesta = Response(status=estado)
		if estado == RESOURCE_CREATED:
			respuesta = Response(
				json.dumps(mascota.jsonificar()),
				status=estado,
				mimetype="application/json"
			)
	return respuesta


@rutas_mascota.get("/mascotas")
def buscar_mascotas():
	respuesta = Response(status=NO_CONTENT)
	nombre = request.args.get("nombre", default=None, type=str)
	especie = request.args.get("especie", default=None, type=str)
	pagina = request.args.get("pagina", default=0, type=int)
	mascotas = Mascota.buscar(nombre, especie, pagina)
	if mascotas:
		url = "https://amigosinformaticos.ddns.net:42070/mascotas?"
		if nombre is not None:
			url += f"nombre={nombre}&"
		if especie is not None:
			url += f"especie={especie}&"
		json_respuesta = {
			"mascotas": mascotas,
			"sig": url + f"pagina={pagina + 1}"
		}
		if pagina > 0:
			json_respuesta["prev"] = url + f"pagina={pagina - 1}"
		respuesta = Response(
			json.dumps(json_respuesta),
			status=OK,
			mimetype="application/json"
		)
	return respuesta


@rutas_mascota.get("/mascotas/<id_mascota>")
def obtener_mascota(id_mascota):
	respuesta = Response(status=NOT_FOUND)
	solicitados = request.json
	mascota = Mascota()
	mascota.id_mascota = id_mascota
	if mascota.cargar():
		respuesta = Response(
			json.dumps(mascota.jsonificar(solicitados)),
			status=OK,
			mimetype="application/json"
		)
	return respuesta


@rutas_mascota.post("/mascotas/<id_mascota>")
@Auth.requires_token
def actualizar_mascota(id_mascota):
	respuesta = Response(status=NOT_FOUND)
	nuevos_valores = request.json
	mascota = Mascota()
	mascota.id_mascota = id_mascota
	if mascota.cargar():
		mascota.cargar_de_json(nuevos_valores)
		respuesta = Response(
			json.dumps(mascota.jsonificar()),
			status=OK,
			mimetype="application/json"
		)
	return respuesta


@rutas_mascota.delete("/mascotas/<id_mascota>")
@Auth.requires_token
def eliminar_mascota(id_mascota):
	mascota = Mascota()
	mascota.id_mascota = id_mascota
	return Response(status=mascota.eliminar())


@rutas_mascota.post("/mascotas/<id_mascota>/imagen")
@Auth.requires_token
def subir_imagen(id_mascota):
	respuesta = Response(status=NOT_FOUND)
	mascota = Mascota()
	mascota.id_mascota = id_mascota
	if mascota.cargar():
		file = request.files["imagen"]
		estado = mascota.guardar_imagen(file.stream)
		file.close()
		respuesta = Response(status=estado)
	return respuesta


@rutas_mascota.get("/mascotas/<id_mascota>/imagen/<id_imagen>")
def obtener_imagen(id_mascota, id_imagen):
	respuesta = Response(status=NOT_FOUND)
	mascota = Mascota()
	mascota.id_mascota = id_mascota
	estado, imagen = mascota.obtener_imagen(id_imagen)
	respuesta = Response(status=estado)
	if estado == OK:
		abierto = open(imagen.name, "rb")
		respuesta = send_file(
			io.BytesIO(abierto.read()),
			mimetype="image/png",
			as_attachment=False
		)
		abierto.close()
	return respuesta


@rutas_mascota.delete("/mascotas/<id_mascota>/imagen/<id_imagen>")
@Auth.requires_token
def eliminar_imagen(id_mascota, id_imagen):
	mascota = Mascota()
	mascota.id_mascota = id_mascota
	return Response(status=mascota.eliminar_imagen(id_imagen))
