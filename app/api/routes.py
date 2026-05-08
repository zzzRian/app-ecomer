"""API JSON: chatbot y endpoints auxiliares."""
from flask import Blueprint, request, jsonify, current_app
from app import csrf
from app.models import Producto

api_bp = Blueprint("api", __name__)

# El chatbot acepta POST sin CSRF para simplificar la integración JS
@api_bp.route("/chatbot", methods=["POST"])
@csrf.exempt
def chatbot():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip().lower()
    if not msg:
        return jsonify({"reply": "¿En qué puedo ayudarte?"})

    # 1) Si hay clave OpenAI configurada, usarla
    api_key = current_app.config.get("OPENAI_API_KEY")
    if api_key:
        try:
            import requests as r
            resp = r.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role":"system","content":"Eres un asistente de una tienda de electrónicos. Responde breve y útil en español."},
                        {"role":"user","content": msg},
                    ],
                }, timeout=15,
            )
            if resp.ok:
                return jsonify({"reply": resp.json()["choices"][0]["message"]["content"]})
        except Exception as e:
            current_app.logger.warning(f"OpenAI fallback: {e}")

    # 2) Reglas locales
    if any(w in msg for w in ["hola","buenas","saludos"]):
        return jsonify({"reply": "¡Hola! 👋 Soy el asistente de la tienda. ¿Buscas algo en particular?"})
    if "envio" in msg or "envío" in msg or "entrega" in msg:
        return jsonify({"reply": "Hacemos envíos a todo el país. Pedidos sobre S/200 tienen envío gratis 🚚."})
    if "pago" in msg:
        return jsonify({"reply": "Aceptamos tarjeta, Yape y efectivo contra entrega."})
    if "garantía" in msg or "garantia" in msg:
        return jsonify({"reply": "Todos los productos incluyen 1 año de garantía oficial."})
    if "recomienda" in msg or "recomendación" in msg or "recomendacion" in msg:
        top = Producto.query.filter_by(destacado=True, activo=True).limit(3).all()
        if top:
            txt = ", ".join(f"{p.nombre} (S/{p.precio_final:.2f})" for p in top)
            return jsonify({"reply": f"Te recomiendo: {txt}"})
    if "precio" in msg or "cuanto" in msg or "cuánto" in msg:
        return jsonify({"reply": "Tenemos productos desde S/99. ¿Qué categoría te interesa: smartphones, laptops, audio o TVs?"})
    return jsonify({"reply": "No estoy seguro de entenderte 🤔. Puedes preguntar por envíos, pagos, garantías o recomendaciones."})
