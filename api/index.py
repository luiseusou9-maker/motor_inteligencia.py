import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS': return '', 200
    try:
        data = request.json
        url = data.get('url')

        # PROMPT MESTRE: Analisa o perfil e gera leads em um único tiro
        prompt_unico = (
            f"Analise o site {url}. Identifique o setor e o perfil de cliente.\n"
            "Com base nisso, gere 5 leads REAIS de alta conversão.\n"
            "REGRAS:\n"
            "1. Tudo em PORTUGUÊS.\n"
            "2. Estime CARGO e SALÁRIO real para o setor.\n"
            "3. MOMENTO: 'Pronto para comprar' ou 'Pesquisando'.\n"
            "4. DDD: Use o da região (ex: 19 para Campinas).\n"
            "Retorne APENAS JSON:\n"
            "{'leads': [{'nome': '...', 'cargo': '...', 'salario': 'R$ ...', 'momento': '...', 'telefone': '...', 'classe': 'A', 'produto': '...', 'tatica': '...'}]}"
        )

        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um Analista de Vendas e Head de Growth de Elite."},
                      {"role": "user", "content": prompt_unico}],
            model="llama-3.1-8b-instant", # Modelo ultra-rápido para evitar Erro 500
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(res.choices[0].message.content).get("leads", [])

        # Salva no banco (Silencioso para não atrasar)
        for l in leads:
            try:
                supabase.table("leads_hiper_assertivos").insert({
                    "empresa_origem": url,
                    "nome_lead": l.get("nome"),
                    "telefone": l.get("telefone"),
                    "classe_social": f"{l.get('classe')} ({l.get('salario')})",
                    "produto_sugerido": f"{l.get('produto')} | {l.get('cargo')}",
                    "estagio_compra": l.get("momento"),
                    "tatica_abordagem": l.get("tatica")
                }).execute()
            except: pass

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app