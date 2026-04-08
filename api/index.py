import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Inicialização
client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS': return '', 200
    try:
        data = request.json
        url_alvo = data.get('url')

        # MODELO 8B-INSTANT: Rápido o suficiente para não dar Erro 500
        prompt_completo = (
            f"Analise minuciosamente o site {url_alvo}. "
            "1. Identifique o produto e o ticket médio real. "
            "2. Rastreie 5 leads (nomes reais brasileiros) com intenção de compra. "
            "3. Se o site for local (ex: Campinas), use DDD 19. "
            "4. Classifique em A, B ou C conforme o bolso necessário para o produto. "
            "Retorne APENAS JSON: {'leads': [{'nome': '...', 'telefone': '...', 'classe': '...', 'produto': '...', 'tatica': '...'}]}"
        )

        res = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um Analista Comercial de Elite. Seja minucioso e use dados brasileiros reais."},
                      {"role": "user", "content": prompt_completo}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        lista_leads = json.loads(res.choices[0].message.content).get("leads", [])

        # Salva no Banco
        for l in lista_leads:
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url_alvo,
                "nome_lead": l.get("nome"),
                "telefone": l.get("telefone"),
                "classe_social": l.get("classe"),
                "produto_sugerido": l.get("produto"),
                "tatica_abordagem": l.get("tatica"),
                "estagio_compra": "Intenção Ativa"
            }).execute()

        return jsonify({"status": "sucesso", "dados": lista_leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app