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

        # COMANDO SUPREMO: FOCO NO LINK E HIERARQUIA A -> B -> C
        prompt = (
            f"AJA COMO UM SNIPER COMERCIAL. ACESSE O SITE: {url}\n"
            "PASSO 1: Identifique EXATAMENTE o que é vendido. Se for imobiliária, veja os bairros e tipos de casas.\n"
            "PASSO 2: Gere 30 leads (10 A+, 10 B, 10 C) que comprariam EXATAMENTE o que está no site.\n"
            "REGRAS DE FERRO:\n"
            "1. PRODUTO: Use nomes de produtos/bairros reais do site. Proibido inventar TI, limpeza ou eletrônicos.\n"
            "2. HIERARQUIA: Organize o JSON começando pelos leads RANK A+, depois B, depois C.\n"
            "3. REALISMO: Rank A+ (R$ 80k+), Rank B (R$ 15k-40k), Rank C (R$ 5k-12k).\n"
            "4. SOCIAL: Gere links de busca (Instagram/LinkedIn) para o nome e cargo do lead.\n"
            "Retorne APENAS o JSON: {'leads': [{'nome': '...', 'cargo': '...', 'salario': '...', 'momento': '...', 'telefone': '...', 'classe': '...', 'produto': '...', 'social': '...', 'tatica': '...'}]}"
        )

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um robô de extração de dados de inventário. Você não alucina. Você só cria leads baseados nos produtos reais do link fornecido."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(completion.choices[0].message.content).get("leads", [])

        # Salva no banco silenciosamente
        for l in leads:
            try:
                supabase.table("leads_hiper_assertivos").insert({
                    "empresa_origem": url,
                    "nome_lead": l.get("nome"),
                    "telefone": l.get("telefone"),
                    "classe_social": f"{l.get('classe')} ({l.get('salario')})",
                    "produto_sugerido": l.get("produto"),
                    "estagio_compra": l.get("momento")
                }).execute()
            except: pass

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app