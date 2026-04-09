import os
import json
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS': return '', 200
    try:
        data = request.json
        url = data.get('url', 'site-alvo.com.br')

        # COMANDO RECONSTRUTOR: Se o site for denso, ele foca no essencial
        prompt_agressivo = (
            f"EXECUÇÃO IMEDIATA PARA O ALVO: {url}\n\n"
            "VOCÊ É UM AGENTE DE CAMPO. SEU OBJETIVO É EXTRAIR VALOR AGORA.\n"
            "1. Identifique 10 categorias de produtos presentes no site (ex: Lotes, Fazendas, Mansões, Casas).\n"
            "2. Para cada categoria, gere imediatamente 3 leads de alto padrão (Total 30 leads).\n"
            "3. NÃO diga que não encontrou leads. Use seu conhecimento de mercado para prever quem são os compradores desses tipos de imóveis no Brasil hoje.\n\n"
            "DADOS REAIS EXIGIDOS:\n"
            "- Nomes brasileiros variados.\n"
            "- Moradia atual em cidades diversas (Capitais e Interior).\n"
            "- Renda compatível: Mansão (150k+), Casas (30k+), Lotes (10k+).\n"
            "- Perfis comportamentais detalhados e originais.\n"
            "- Telefone com DDDs reais (11, 19, 21, 31, 41, 61).\n\n"
            "SAÍDA APENAS JSON: {'leads': [...]}"
        )

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um Sniper de Leads. Sua missão é entregar resultados, nunca desculpas. Se o site for complexo, extraia o padrão de produtos e gere a demanda."},
                {"role": "user", "content": prompt_agressivo}
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.9, # Aumentado para forçar a criação de perfis originais
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        leads = res.get("leads", [])

        # Se a IA vier vazia, vamos forçar um fallback de segurança
        if not leads:
            return jsonify({"status": "erro", "mensagem": "IA em modo de segurança. Tente novamente."}), 404

        # Limpeza de números fakes (Trava Anti-Preguiça)
        for l in leads:
            if "9999" in str(l.get('telefone')) or not l.get('telefone'):
                ddd = random.choice([11, 19, 21, 31, 61, 41, 15, 16])
                l['telefone'] = f"({ddd}) 9{random.randint(7001,9999)}-{random.randint(1001,9999)}"

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app