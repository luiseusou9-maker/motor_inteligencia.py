import os
from flask import Flask, jsonify
from flask_cors import CORS
import googlemaps
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# --- SUAS CHAVES ---
GOOGLE_MAPS_KEY = "AIzaSyDpHmD-5MipOLNo9NaDW2om5JcMwe0r93k"
SUPABASE_URL = "https://qxcofhizzbedwawwvoxu.supabase.co"
SUPABASE_KEY = "COLE_AQUI_A_SUA_SERVICE_ROLE_KEY" # Aquela última que você me mandou

gmaps = googlemaps.Client(key=GOOGLE_MAPS_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/minerar', methods=['GET'])
def minerar():
    try:
        # 1. Busca clínicas no Cambuí pelo Google
        busca = gmaps.places(query='clínicas no Cambuí, Campinas', language='pt-BR')
        resultados = busca.get('results', [])
        
        novos_leads = []
        for lugar in resultados[:10]: # Pegando as 10 primeiras
            lead = {
                "nome": lugar.get('name'),
                "endereco": lugar.get('formatted_address'),
                "nota_google": lugar.get('rating'),
                "status_contato": "Novo"
            }
            novos_leads.append(lead)
            
            # 2. Salva direto no Banco de Dados (Supabase)
            supabase.table("leads_prospeccao").insert(lead).execute()
            
        return jsonify({
            "status": "sucesso", 
            "mensagem": f"{len(novos_leads)} leads minerados e salvos no banco!",
            "leads": novos_leads
        })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})

@app.route('/api')
def home():
    return jsonify({"projeto": "RITT Intelligence", "status": "Motor Conectado ao Banco"})