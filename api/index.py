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

        # PROMPT EVOLUÍDO: IDENTIFICAÇÃO DE NICHO E SEGMENTAÇÃO A/B/C
        prompt = (
            f"Analise o site {url}. Identifique o NICHO (Ex: Carros, Imóveis, Estética) e os produtos.\n"
            "Gere 15 leads REAIS e segmentados (5 A+, 5 B, 5 C).\n"
            "REGRAS DE OURO:\n"
            "1. ENCAIXE: Relacione o lead a um produto específico do site que caiba no bolso dele.\n"
            "2. PERFIL SOCIAL: Gere links de busca (Instagram/LinkedIn) baseados no nome e cargo.\n"
            "3. MOMENTO: Identifique quem está 'Pronto para comprar' ou 'Pesquisando'.\n"
            "4. DDD: Regionalize conforme o site (Ex: 19 para Campinas).\n"
            "Retorne APENAS JSON: {'leads': [{'nome': '...', 'cargo': '...', 'salario': '...', 'momento': '...', 'telefone': '...', 'classe': '...', 'produto': '...', 'social': '...', 'tatica': '...'}]}"
        )

        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um Head de Vendas focado em análise de mercado e segmentação de renda. Responda apenas JSON."},
                      {"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", # Estabilidade total
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(completion.choices[0].message.content).get("leads", [])

        # Persistência no Supabase
        for l in leads:
            try:
                supabase.table("leads_hiper_assertivos").insert({
                    "empresa_origem": url,
                    "nome_lead": l.get("nome"),
                    "telefone": l.get("telefone"),
                    "classe_social": f"{l.get('classe')} ({l.get('salario')})",
                    "produto_sugerido": f"{l.get('produto')} | {l.get('cargo')}",
                    "estagio_compra": l.get("momento"),
                    "tatica_abordagem": l.get("social")
                }).execute()
            except: pass

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app