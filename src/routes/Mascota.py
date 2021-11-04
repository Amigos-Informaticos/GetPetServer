import json

from flask import Blueprint, Response, request

from src.model.Mascota import Mascota
from src.routes.Auth import Auth
from src.routes.HTTPStatus import NOT_FOUND, NO_CONTENT, OK

rutas_mascota = Blueprint("rutas_mascota", __name__)


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
@Auth.requires_token
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