import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Inicialização direta
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS': return '', 200
    try:
        data = request.json
        url = data.get('url')

        # PROMPT ÚNICO E AGRESSIVO: Foco em Riqueza e Imóveis do Site
        prompt = (
            f"Analise o site {url}. Identifique os imóveis de luxo.\n"
            "Gere 10 leads de CLASSE A+ (Donos de empresas, CEOs, Médicos).\n"
            "REGRAS:\n"
            "1. SALÁRIO: Acima de R$ 50.000,00.\n"
            "2. PRODUTO: Vincule o lead a um imóvel específico do site.\n"
            "3. DDD: Use 19 para Campinas ou a região do site.\n"
            "4. Responda APENAS JSON:\n"
            "{'leads': [{'nome': '...', 'cargo': '...', 'salario': '...', 'momento': '...', 'telefone': '...', 'classe': 'A+', 'produto': '...', 'tatica': '...'}]}"
        )

        # Usando o modelo mais rápido para GARANTIR que não dê Erro 500
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "Analista comercial de luxo. Responda apenas JSON."},
                      {"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(completion.choices[0].message.content).get("leads", [])

        # Registro no Banco
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