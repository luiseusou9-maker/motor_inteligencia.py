import os
from flask import Flask, jsonify
from flask_cors import CORS
import googlemaps
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# Função de Verificação de Saúde das Chaves
def get_db_and_maps():
    # Buscando nomes EXATOS conforme seus prints da Vercel
    m_key = os.getenv("Maps_KEY")
    s_url = os.getenv("SUPABASE_URL")
    s_key = os.getenv("SUPABASE_KEY")
    
    if not all([m_key, s_url, s_key]):
        raise ValueError(f"Faltando Variáveis: Maps:{bool(m_key)}, URL:{bool(s_url)}, Key:{bool(s_key)}")
    
    gmaps = googlemaps.Client(key=m_key)
    supabase = create_client(s_url, s_key)
    return gmaps, supabase

@app.route('/api/minerar', methods=['GET'])
def minerar():
    try:
        gmaps, supabase = get_db_and_maps()
        
        # Busca Elite
        busca = gmaps.places(query='clínicas no Cambuí, Campinas', language='pt-BR')
        resultados = busca.get('results', [])
        
        leads_processados = []
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
            leads_processados.append(lead)
            
        return jsonify({"status": "sucesso", "total": len(leads_processados)})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/leads', methods=['GET'])
def listar():
    try:
        _, supabase = get_db_and_maps()
        res = supabase.table("leads_cambui").select("*").order('id', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api')
def health():
    return jsonify({"status": "online", "engine": "RITT Intelligence Pro"})