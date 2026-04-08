import os
from flask import Flask, jsonify
from flask_cors import CORS
import googlemaps
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES (Suas chaves já estão aqui) ---
GOOGLE_MAPS_KEY = "AIzaSyDpHmD-5MipOLNo9NaDW2om5JcMwe0r93k"
SUPABASE_URL = "https://qxcofhizzbedwawwvoxu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4Y29maGl6emJlZHdhd3d2b3h1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTY2NDk2NiwiZXhwIjoyMDkxMjQwOTY2fQ.UVhweBNh29dWAvgbKQe1aP2hSDXxUbxMs9pP5GytWH0"

# Inicializa as ferramentas
gmaps = googlemaps.Client(key=GOOGLE_MAPS_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/minerar', methods=['GET'])
def minerar():
    try:
        # 1. Busca clínicas no Cambuí
        # O Google Maps exige que a gente use o endereço do site para validar a chave
        busca = gmaps.places(query='clínicas no Cambuí, Campinas', language='pt-BR')
        resultados = busca.get('results', [])
        
        leads_processados = []
        for lugar in resultados[:10]:
            # Pega o telefone (Place Details)
            detalhes = gmaps.place(place_id=lugar['place_id'], fields=['formatted_phone_number'])
            telefone = detalhes.get('result', {}).get('formatted_phone_number', 'Sem telefone')

            lead = {
                "nome": lugar.get('name'),
                "endereco": lugar.get('formatted_address'),
                "telefone": telefone,
                "status": "Pendente"
            }
            
            # 2. Grava no Supabase (Tabela leads_cambui)
            supabase.table("leads_cambui").insert(lead).execute()
            leads_processados.append(lead)
            
        return jsonify({
            "status": "sucesso", 
            "mensagem": f"🦅 RITT Intel: {len(leads_processados)} leads capturados!",
            "dados": leads_processados
        })
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)})

@app.route('/api')
def home():
    return jsonify({"projeto": "RITT Intelligence", "engine": "Python 3.14", "banco": "Conectado"})