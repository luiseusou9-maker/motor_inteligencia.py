import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Puxando as chaves que o Llama e o Supabase exigem
GROQ_KEY = os.environ.get("GROQ_API_KEY")
S_URL = os.environ.get("SUPABASE_URL")
S_KEY = os.environ.get("SUPABASE_KEY")

# Inicializando os comandos
client_groq = Groq(api_key=GROQ_KEY)
supabase = create_client(S_URL, S_KEY)

@app.route('/api/analisar', methods=['POST'])
def processar_maquina():
    data = request.json
    url_alvo = data.get('url')
    
    if not url_alvo:
        return jsonify({"error": "Link ausente"}), 400

    try:
        # 1. O Llama entra em campo para reconhecer o território
        analise = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": f"Resuma o foco comercial deste site em uma frase curta: {url_alvo}"}],
            model="llama-3.1-8b-instant", # O novo motor que ele gosta
        )
        setor_info = analise.choices[0].message.content

        # 2. O Llama gera os leads com precisão cirúrgica
        leads_raw = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um minerador de elite. Responda APENAS JSON."},
                {"role": "user", "content": f"Gere 3 leads assertivos para o setor {setor_info}. Formato: {{'leads': [{{'nome': '...', 'telefone': '...', 'prioridade': 'Alta', 'score': 10, 'tatica': '...'}}]}}"}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        dados_json = json.loads(leads_raw.choices[0].message.content)
        lista_leads = dados_json.get("leads", [])

        # 3. O Salve no Banco (Sem erro de permissão)
        for lead in lista_leads:
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url_alvo,
                "setor_identificado": setor_info[:150],
                "nome_lead": lead.get("nome"),
                "telefone": lead.get("telefone"),
                "prioridade": lead.get("prioridade"),
                "score_assertividade": lead.get("score"),
                "tatica_abordagem": lead.get("tatica")
            }).execute()

        return jsonify({
            "status": "Sucesso", 
            "leads_capturados": len(lista_leads),
            "dados": lista_leads
        })

    except Exception as e:
        # Se ele der qualquer "chilique", a gente pega aqui
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()