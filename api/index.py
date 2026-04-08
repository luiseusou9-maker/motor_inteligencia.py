import os
from flask import Flask, jsonify
from flask_cors import CORS
import googlemaps
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# --- ARQUITETURA DE SEGURANÇA ---
def iniciar_servicos():
    # Puxa as chaves do cofre da Vercel que você configurou
    m_key = os.getenv("Maps_KEY")
    s_url = os.getenv("SUPABASE_URL")
    s_key = os.getenv("SUPABASE_KEY")
    
    if not all([m_key, s_url, s_key]):
        raise ValueError("Chaves ausentes no ambiente da Vercel")
        
    gmaps = googlemaps.Client(key=m_key)
    supabase = create_client(s_url, s_key)
    return gmaps, supabase

@app.route('/api/minerar', methods=['GET'])
def minerar():
    try:
        gmaps, supabase = iniciar_servicos()
        
        # Busca qualificada: Clínicas no Cambuí
        busca = gmaps.places(query='clínicas no Cambuí, Campinas', language='pt-BR')
        resultados = busca.get('results', [])
        
        processados = []
        for lugar in resultados[:10]:
            lead = {
                "nome": lugar.get('name'),
                "endereco": lugar.get('formatted_address'),
                "status": "Pendente"
            }
            # Gravação direta no banco
            supabase.table("leads_cambui").insert(lead).execute()
            processados.append(lead)
            
        return jsonify({"status": "sucesso", "total": len(processados)})
    except Exception as e:
        # Se der erro, ele explica o motivo em vez de só dar 500
        return jsonify({"status": "erro", "detalhes": str(e)}), 500

@app.route('/api/leads', methods=['GET'])
def listar():
    try:
        _, supabase = iniciar_servicos()
        res = supabase.table("leads_cambui").select("*").order('id', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api')
def home():
    return jsonify({"projeto": "RITT Intelligence", "engine": "Python 3.14"})