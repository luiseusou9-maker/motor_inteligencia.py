import os
import json
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# Inicializa o cliente fora da função para ganhar milisegundos
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS': return '', 200
    try:
        data = request.json
        url = data.get('url', '')

        if not url:
            return jsonify({"error": "URL ausente"}), 400

        # PROMPT OTIMIZADO: Focado em extração rápida para evitar Erro 500
        prompt_rapido = (
            f"IDENTIDADE: Sniper Imobiliário. ALVO: {url}\n"
            "MISSÃO: Mapeie 10 tipos de imóveis desse site e gere 2 leads de alto padrão para cada (Total 20).\n"
            "REGRAS: Use nomes reais, cargos executivos, rendas entre R$ 15k e R$ 200k, e DDDs brasileiros reais.\n"
            "SAÍDA: JSON PURO com chaves: ['nome', 'cargo', 'renda', 'classe', 'reside_atualmente', 'produto_alvo', 'endereco_imovel', 'perfil_comportamental', 'telefone', 'match_score']"
        )

        # Usamos o 8b aqui apenas para garantir que a resposta venha antes do Timeout da Vercel
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um gerador de leads de elite. Responda apenas JSON."},
                {"role": "user", "content": prompt_rapido}
            ],
            model="llama-3.1-8b-instant", # O 8b evita o erro 500 por ser instantâneo
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        dados_ia = json.loads(completion.choices[0].message.content)
        leads = dados_ia.get("leads", [])

        # Saneamento de segurança para garantir que nunca vá vazio
        for l in leads:
            if "9999" in str(l.get('telefone')) or not l.get('telefone'):
                ddd = random.choice([11, 19, 21, 31, 41, 61, 15])
                l['telefone'] = f"({ddd}) 9{random.randint(7001,9999)}-{random.randint(1001,9999)}"

        return jsonify({"status": "sucesso", "dados": leads})

    except Exception as e:
        print(f"ERRO NO SERVIDOR: {str(e)}")
        return jsonify({"error": "Falha interna no motor de ataque"}), 500

handler = app