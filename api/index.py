import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

# 1. DECLARAÇÃO GLOBAL (O que a Vercel procura)
app = Flask(__name__)
CORS(app)

# Inicialização das chaves
GROQ_KEY = os.environ.get("GROQ_API_KEY")
S_URL = os.environ.get("SUPABASE_URL")
S_KEY = os.environ.get("SUPABASE_KEY")

client_groq = Groq(api_key=GROQ_KEY)
supabase = create_client(S_URL, S_KEY)

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        url_alvo = data.get('url')

        # --- FASE 1: RECONHECIMENTO MINUCIOSO ---
        prompt_recon = (
            f"Aja como um Perito Comercial. Analise a URL {url_alvo} com foco total. "
            "Identifique o nicho, ticket médio e localização. Não tenha pressa."
        )
        recon_res = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt_recon}],
            model="llama-3.1-8b-instant"
        )
        contexto = recon_res.choices[0].message.content

        # --- FASE 2: RASTREIO DE INTENÇÃO REAL ---
        # Usamos o modelo 70b para máxima assertividade
        prompt_rastreio = (
            f"Contexto do Site: {contexto}. "
            "Rastreie 5 leads com intenção real de compra baseada em pesquisas na rede (Google Search). "
            "Separe por Classe A (Luxo), B (Médio/Alto) ou C (Popular). "
            "Retorne APENAS JSON: {'leads': [{'nome': '...', 'telefone': '...', 'classe': '...', 'produto': '...', 'tatica': '...'}]}"
        )

        leads_raw = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um Analista de Big Data. Seja minucioso e use nomes/DDDs brasileiros reais."},
                      {"role": "user", "content": prompt_rastreio}],
            model="llama-3.1-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        lista_leads = json.loads(leads_raw.choices[0].message.content).get("leads", [])

        # --- FASE 3: REGISTRO NO BANCO ---
        for l in lista_leads:
            nome_busca = l.get('nome').replace(' ', '+')
            link_social = f"https://www.google.com/search?q=site:linkedin.com/in/+%22{nome_busca}%22"
            
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url_alvo,
                "setor_identificado": contexto[:300],
                "nome_lead": l.get("nome"),
                "telefone": l.get("telefone"),
                "rede_social": link_social,
                "classe_social": l.get("classe"),
                "produto_sugerido": l.get("produto"),
                "estagio_compra": "Intenção de Busca Ativa",
                "tatica_abordagem": l.get("tatica")
            }).execute()

        return jsonify({"status": "sucesso", "dados": lista_leads})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# IMPORTANTE PARA A VERCEL ENCONTRAR O HANDLER
handler = app