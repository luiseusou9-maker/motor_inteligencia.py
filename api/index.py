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

        # COMANDO ÚNICO E ASSERTIVO - PROTOCOLO IMOBILIÁRIO NACIONAL
        prompt = (
            f"SISTEMA DE INTELIGÊNCIA IMOBILIÁRIA - ALVO: {url}\n\n"
            "PASSO 1: Mapeie o inventário real do site (tipos de imóveis, preços e localizações).\n"
            "PASSO 2: Localize 90 leads reais em todo o Brasil (30 Rank A+, 30 B, 30 C) com intenção de compra nessas áreas.\n\n"
            "REGRAS RÍGIDAS:\n"
            "- ORDEM: O JSON deve vir ordenado por Rank: todos os A+ primeiro, depois B, depois C.\n"
            "- REALISMO: Rank A+ (Renda R$ 100k+), Rank B (R$ 25k-50k), Rank C (R$ 7k-15k).\n"
            "- SEM FRONTEIRAS: O lead pode ser de qualquer estado, desde que o interesse seja no imóvel do site.\n"
            "- DADOS: Nome, Cargo, Salário, WhatsApp Real, Localização de Origem, Produto do Site e Link Social.\n"
            "Retorne APENAS o JSON: {'leads': [...]}"
        )

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um Corretor Digital de Elite. Primeiro você mapeia o estoque do site, depois caça os compradores ideais no Brasil."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(completion.choices[0].message.content).get("leads", [])

        # Salva no banco silenciosamente
        for l in leads:
            try:
                supabase.table("leads_guerra").insert({
                    "url_loja": url,
                    "nome": l.get("nome"),
                    "whatsapp": l.get("telefone"),
                    "perfil": f"{l.get('classe')} - {l.get('salario')}",
                    "imovel": l.get("produto")
                }).execute()
            except: pass

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app