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

        # ETAPA 1: SUA LÓGICA DE ANALISTA EXPERIENTE
        prompt_perfil = f"Analise este link: {url}. Identifique os produtos e o perfil do cliente ideal (Poder aquisitivo, interesses, urgência)."
        analise_perfil = client.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um analista de vendas experiente."},
                      {"role": "user", "content": prompt_perfil}],
            model="llama-3.1-8b-instant"
        ).choices[0].message.content

        # ETAPA 2: CAPTURA DE HIPER LEADS (Com as novas colunas)
        prompt_leads = (
            f"Com base no perfil: {analise_perfil}, gere 5 leads REAIS e prioritários.\n"
            "Retorne APENAS JSON no formato:\n"
            "{'leads': [{'nome': '...', 'cargo': '...', 'salario': 'R$ ...', 'momento': '...', 'telefone': '...', 'classe': 'A', 'produto': '...', 'tatica': '...'}]}"
        )

        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Gere leads assertivos em JSON. Use português."},
                      {"role": "user", "content": prompt_leads}],
            model="llama-3.1-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(res.choices[0].message.content).get("leads", [])

        # SALVANDO NO BANCO (Adaptado para as novas colunas)
        for l in leads:
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url,
                "nome_lead": l.get("nome"),
                "telefone": l.get("telefone"),
                "classe_social": f"{l.get('classe')} ({l.get('salario')})",
                "produto_sugerido": f"{l.get('produto')} | Cargo: {l.get('cargo')}",
                "estagio_compra": l.get("momento"),
                "tatica_abordagem": l.get("tatica")
            }).execute()

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app