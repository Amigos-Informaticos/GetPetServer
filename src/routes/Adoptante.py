import json

from flask import Blueprint, Response, request, session

from src.connection.EasyFTP import EasyFTP
from src.model.Adoptante import Adoptante
from src.routes.Auth import Auth
from src.routes.HTTPStatus import NOT_ACCEPTABLE, NOT_FOUND, OK, RESOURCE_CREATED
from src.util.Util import incluidos

rutas_adoptante = Blueprint("rutas_adoptante", __name__)


@rutas_adoptante.route("/login", methods=["POST"])
def login():
	requeridos: set = {"email", "password"}
	respuesta = Response(status=NOT_ACCEPTABLE)
	valores_json = request.json
	if incluidos(requeridos, valores_json):
		adoptante = Adoptante()
		adoptante.email = valores_json["email"]
		adoptante.set_password(valores_json["password"])
		estado = adoptante.login()
		respuesta = Response(status=estado)
		if estado == OK:
			if adoptante.cargar_adoptante():
				token = Auth.generate_token(adoptante)
				session.permanent = True
				session["token"] = token
				session["email"] = adoptante.email
				session["password"] = adoptante.password
				respuesta = Response(
					json.dumps({
						"token": token,
						"id": adoptante.id_adoptante
					}),
					status=estado,
					mimetype="application/json"
				)
	return respuesta


@rutas_adoptante.route("/adoptantes", methods=["POST"])
def registrar():
	respuesta = Response(status=NOT_ACCEPTABLE)
	requeridos = {"nombre", "sexo"}
	vals = request.json
	if incluidos(requeridos, vals):
		adoptante = Adoptante()
		adoptante.cargar_de_json(vals)
		estado = adoptante.guardar()
		respuesta = Response(status=estado)
		if estado == RESOURCE_CREATED:
			respuesta = Response(
				json.dumps(adoptante.jsonificar()),
				status=estado,
				mimetype="application/json"
			)
	return respuesta


@rutas_adoptante.post("/adoptantes/<id_adoptante>/image")
@Auth.requires_token
def subir_imagen(id_adoptante):
	respuesta = Response(status=NOT_FOUND)
	adoptante = Adoptante()
	adoptante.id_adoptante = id_adoptante
	if adoptante.cargar_adoptante():
		file = request.files["imagen"]
		conexion = EasyFTP.build_from_static()
		guardado = conexion.upload_binary(file.stream, f"{id_adoptante}.png", False)
		file.close()
		resultado = 500
		if guardado:
			resultado = 226
		respuesta = Response(status=resultado)
	return respuesta


@rutas_adoptante.route("/adoptantes/<id_adoptante>", methods=["GET"])
@Auth.requires_token
def get_adoptante(id_adoptante: int):
	respuesta = Response(status=NOT_FOUND)
	vals = request.json
	adoptante = Adoptante()
	adoptante.id_adoptante = id_adoptante
	if adoptante.cargar_adoptante():
		respuesta = Response(
			json.dumps(adoptante.jsonificar(vals)),
			status=OK,
			mimetype="application/json"
		)
	return respuesta


@rutas_adoptante.route("/adoptantes/<id_adoptante>", methods=["POST"])
@Auth.requires_token
def actualizar_adoptante(id_adoptante):
	respuesta = Response(status=NOT_FOUND)
	vals = request.json
	adoptante = Adoptante()
	adoptante.id_adoptante = id_adoptante
	adoptante.cargar_de_json(vals)
	estado = adoptante.actualizar()
	respuesta = Response(status=estado)
	if estado == OK:
		adoptante.cargar_adoptante()
		respuesta = Response(
			json.dumps(adoptante.jsonificar()),
			status=OK,
			mimetype="application/json"
		)
	return respuesta


@rutas_adoptante.delete("/adoptantes/<id_adoptante>")
@Auth.requires_token
def eliminar_adoptante(id_adoptante):
	respuesta = Response(status=NOT_FOUND)
	adoptante = Adoptante()
	adoptante.id_adoptante = id_adoptante
	respuesta = Response(status=adoptante.eliminar())
	return respuesta