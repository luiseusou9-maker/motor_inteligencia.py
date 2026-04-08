import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Carregando chaves da Vercel
GROQ_KEY = os.environ.get("GROQ_API_KEY")
S_URL = os.environ.get("SUPABASE_URL")
S_KEY = os.environ.get("SUPABASE_KEY")

# Inicializando clientes
client_groq = Groq(api_key=GROQ_KEY)
supabase = create_client(S_URL, S_KEY)

@app.route('/api/analisar', methods=['POST'])
def processar_maquina():
    data = request.json
    url_alvo = data.get('url')
    
    if not url_alvo:
        return jsonify({"error": "Link ausente"}), 400

    try:
        # 1. Inteligência de Campo (Glock analisa o site)
        analise = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": f"Resuma em 10 palavras o que este site vende e qual o público: {url_alvo}"}],
            model="llama3-8b-8192",
        )
        setor_info = analise.choices[0].message.content

        # 2. Mineração de Leads (Glock gera os dados em JSON)
        prompt_leads = (
            f"Gere um JSON com 3 leads fictícios mas altamente assertivos para o setor {setor_info}. "
            "Formato: {'leads': [{'nome': '...', 'telefone': '...', 'prioridade': 'Alta', 'score': 10, 'tatica': '...'}]}"
        )
        
        leads_raw = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": "Responda apenas com JSON puro."},
                      {"role": "user", "content": prompt_leads}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        
        dados_json = json.loads(leads_raw.choices[0].message.content)
        lista_leads = dados_json.get("leads", [])

        # 3. Registro no Supabase (O Salve do Ouro)
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
            "status": "Finalizado", 
            "leads_capturados": len(lista_leads),
            "dados": lista_leads
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()