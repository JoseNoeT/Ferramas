from __future__ import annotations

from datetime import datetime

import requests
from django.utils import timezone

MINDICADOR_API_URL = "https://mindicador.cl/api"
MINDICADOR_TIMEOUT_SECONDS = 5


def _fecha_actual_iso():
	return timezone.now().isoformat()


def _extraer_valor_indicador(payload, clave):
	indicador = payload.get(clave) if isinstance(payload, dict) else None
	if not isinstance(indicador, dict):
		return None
	valor = indicador.get("valor")
	return valor if isinstance(valor, (int, float)) else None


def _extraer_fecha_consulta(payload):
	if not isinstance(payload, dict):
		return _fecha_actual_iso()

	fecha = payload.get("fecha")
	if isinstance(fecha, str):
		try:
			parsed = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
			if timezone.is_naive(parsed):
				parsed = timezone.make_aware(parsed)
			return parsed.isoformat()
		except ValueError:
			return _fecha_actual_iso()
	return _fecha_actual_iso()


def consultar_indicadores_economicos():
	"""Consulta UF, dolar, euro y UTM desde mindicador.cl sin propagar fallas al sistema."""
	respuesta_base = {
		"uf": None,
		"dolar": None,
		"euro": None,
		"utm": None,
		"fecha_consulta": _fecha_actual_iso(),
		"fuente": MINDICADOR_API_URL,
	}

	try:
		response = requests.get(MINDICADOR_API_URL, timeout=MINDICADOR_TIMEOUT_SECONDS)
		response.raise_for_status()
		payload = response.json()
	except (requests.RequestException, ValueError):
		return respuesta_base

	respuesta_base["uf"] = _extraer_valor_indicador(payload, "uf")
	respuesta_base["dolar"] = _extraer_valor_indicador(payload, "dolar")
	respuesta_base["euro"] = _extraer_valor_indicador(payload, "euro")
	respuesta_base["utm"] = _extraer_valor_indicador(payload, "utm")
	respuesta_base["fecha_consulta"] = _extraer_fecha_consulta(payload)
	return respuesta_base
