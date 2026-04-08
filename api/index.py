import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Conexões
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS': return '', 200
    
    try:
        url = request.json.get('url')
        
        # Comando seco e direto para a IA não errar o nicho
        prompt = f"Analise o site {url}. É imobiliária de luxo. Gere 5 leads (Investidores) em Campinas (DDD 19). Responda apenas JSON: {{'leads': [{{'nome': '...', 'telefone': '...', 'classe': 'A', 'produto': 'Mansão', 'tatica': 'VIP'}}]}}"

        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        import json
        leads = json.loads(completion.choices[0].message.content).get("leads", [])

        # Salva rápido no banco
        for l in leads:
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url, "nome_lead": l.get("nome"), "telefone": l.get("telefone"),
                "classe_social": l.get("classe"), "produto_sugerido": l.get("produto"), "tatica_abordagem": l.get("tatica")
            }).execute()

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500