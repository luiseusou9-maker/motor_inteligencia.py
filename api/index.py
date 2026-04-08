import os
from flask import Flask, jsonify
from flask_cors import CORS
import googlemaps
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES ---
GOOGLE_MAPS_KEY = "AIzaSyDpHmD-5MipOLNo9NaDW2om5JcMwe0r93k"
SUPABASE_URL = "https://qxcofhizzbedwawwvoxu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4Y29maGl6emJlZHdhd3d2b3h1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTY2NDk2NiwiZXhwIjoyMDkxMjQwOTY2fQ.UVhweBNh29dWAvgbKQe1aP2hSDXxUbxMs9pP5GytWH0"

gmaps = googlemaps.Client(key=GOOGLE_MAPS_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/minerar', methods=['GET'])
def minerar():
    try:
        busca = gmaps.places(query='clínicas no Cambuí, Campinas', language='pt-BR')
        resultados = busca.get('results', [])
        
        for lugar in resultados[:10]:
            detalhes = gmaps.place(place_id=lugar['place_id'], fields=['formatted_phone_number'])
            telefone = detalhes.get('result', {}).get('formatted_phone_number', 'Sem telefone')
            
            lead = {
                "nome": lugar.get('name'),
                "endereco": lugar.get('formatted_address'),
                "telefone": telefone,
                "status": "Pendente"
            }
            supabase.table("leads_cambui").insert(lead).execute()
            
        return jsonify({"status": "sucesso", "mensagem": "Leads minerados!"})
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)})

@app.route('/api/leads', methods=['GET'])
def listar_leads():
    # Essa rota serve para a sua tela azul puxar os dados do banco
    try:
        resposta = supabase.table("leads_cambui").select("*").execute()
        return jsonify(resposta.data)
    except Exception as e:
        return jsonify([])

@app.route('/api')
def home():
    return jsonify({"projeto": "RITT Intelligence", "status": "Online"})