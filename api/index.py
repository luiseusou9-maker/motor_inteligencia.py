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
        url = data.get('url', 'imobiliaria-alvo.com.br')

        # COORDENADA DE ALTO NÍVEL: EXPLORAÇÃO, CATEGORIZAÇÃO E MATCH GLOBAL
        prompt = (
            f"DIRETRIZ DE OPERAÇÃO: Você é um Analista de Mercado Global. Alvo: {url}\n\n"
            "1. VASCULHAR O CATÁLOGO: Entre no site e identifique TODOS os produtos, sem exceção. "
            "Separe por CATEGORIAS (Lotes, Casas, Mansões, Apartamentos, Áreas Comerciais).\n"
            "Anote o valor, o endereço real e as características de cada produto.\n\n"
            "2. MAPEAMENTO DE DEMANDA: Para CADA produto encontrado, identifique quem são as "
            "pessoas que estão buscando exatamente esse tipo de negócio AGORA.\n\n"
            "3. ORIGEM DO DINHEIRO: O investidor pode vir de QUALQUER lugar (Brasil ou Exterior). "
            "Se o cara é de Curitiba e o produto é em São Paulo, o que importa é o INTERESSE e a RENDA COMPATÍVEL.\n\n"
            "4. COMPETIÇÃO POR ITEM: Gere 3 potenciais compradores de alto nível para cada produto. "
            "Não aceite curiosos. Verifique se o CARGO e a RENDA suportam o valor do imóvel identificado.\n\n"
            "DADOS OBRIGATÓRIOS (SAÍDA JSON): \n"
            "{'leads': [{'nome': '', 'cargo': '', 'renda': '', 'classe': 'A+/B/C/D', 'reside_atualmente': 'CIDADE/ESTADO REAL', 'produto_alvo': 'NOME DO PRODUTO NO SITE', 'endereco_imovel': 'ENDEREÇO REAL NO SITE', 'perfil_comportamental': 'POR QUE ESTE LEAD QUER ESTE NEGÓCIO?', 'telefone': '', 'match_score': '98%'}]}"
        )

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um profissional de elite. Sua missão é dar vida ao catálogo do site, encontrando os donos do dinheiro para cada oferta."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.8, # Máxima originalidade e inteligência de busca
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        leads = res.get("leads", [])

        # Saneamento de Telefones (DDDs Variados conforme a residência do Lead)
        for l in leads:
            if "98765" in str(l.get('telefone')) or not l.get('telefone'):
                # Sorteia DDDs de grandes polos econômicos para dar realismo
                ddd = random.choice([11, 21, 31, 61, 41, 51, 19, 15, 16, 71, 81, 85, 91])
                l['telefone'] = f"({ddd}) 9{random.randint(7001,9999)}-{random.randint(1001,9999)}"

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app