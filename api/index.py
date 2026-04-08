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

        # COMANDO DE FERRO: LEITURA REAL E ENCAIXE DE INVENTÁRIO
        prompt = (
            f"COMANDO PRIORITÁRIO: Analise o inventário real do site {url}.\n"
            "Se for imobiliária, extraia tipos de imóveis e bairros. Se for carros, marcas e modelos.\n"
            "Gere 15 leads REAIS (5 A+, 5 B, 5 C) baseados no conteúdo DESTE SITE específico.\n"
            "PROIBIDO: Não invente serviços de TI ou cargos genéricos se o site não for disso.\n"
            "DETALHES OBRIGATÓRIOS:\n"
            "1. PRODUTO: Cite um item específico que está no site (Ex: Casa no Gramado, Porsche 911).\n"
            "2. SALÁRIO: A+ (>R$80k), B (R$15k-R$40k), C (R$5k-R$12k).\n"
            "3. SOCIAL: Link real de busca no Instagram/LinkedIn.\n"
            "4. DDD: Use o DDD 19 se o site for de Campinas.\n"
            "Retorne APENAS JSON: {'leads': [{'nome': '...', 'cargo': '...', 'salario': '...', 'momento': '...', 'telefone': '...', 'classe': '...', 'produto': '...', 'social': '...', 'tatica': '...'}]}"
        )

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um Sniper de Vendas. Você nunca inventa dados genéricos. Você extrai o DNA do site e encontra o comprador exato para o que está na tela."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(completion.choices[0].message.content).get("leads", [])

        # Persistência
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