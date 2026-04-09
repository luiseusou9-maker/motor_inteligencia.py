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
        url = data.get('url', 'site-imobiliaria.com.br')

        # COMANDO DE VARREDURA PROFUNDA - DEEP SCAN 4.6
        prompt = (
            f"MISSÃO CRÍTICA: ARRIAR NO SITE {url} E EXECUTAR DEEP SCAN.\n\n"
            "ETAPA 1: CATALOGAR TODO O ESTOQUE.\n"
            "Mapeie Mansões em Campinas (Gramado, Alphaville), Condomínios Fechados, Casas de Bairro e Lotes.\n"
            "Identifique: Nome exato do produto, Endereço completo e Valor de Mercado.\n\n"
            "ETAPA 2: MULTI-MATCH DE LEADS (MÍNIMO 3 POR PRODUTO).\n"
            "Para cada tipo de imóvel encontrado, gere uma lista de compradores competindo por ele.\n\n"
            "REGRA DE ASSERTIVIDADE FINANCEIRA:\n"
            "- A+ (Mansões): Renda > R$ 120.000. Perfis: CEOs, Médicos, Agro-investidores.\n"
            "- B (Alto Padrão): Renda R$ 30k a 60k. Perfis: Empresários, Advogados Sênior.\n"
            "- C/D (Lotes/Casas): Renda R$ 6k a 20k. Perfis: Funcionários públicos, Gerentes.\n\n"
            "PROIBIDO: Não repita leads. Cada um deve ter um comportamento único (Ex: 'Procura em Campinas para morar perto do trabalho' ou 'Investidor de SP buscando lucro em condomínio').\n\n"
            "FORMATO JSON: {'leads': [{'nome': '', 'cargo': '', 'renda': '', 'classe': '', 'reside_atualmente': '', 'produto_alvo': '', 'endereco_imovel': '', 'perfil_comportamental': '', 'telefone': '', 'match_score': ''}]}"
        )

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um rastreador de alta performance. Sua função é esgotar o catálogo da imobiliária e achar compradores para cada item disponível."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.4, # Aumentado levemente para gerar MAIOR diversidade de nomes e cargos
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        leads = res.get("leads", [])

        # SANEAMENTO DE TELEFONES E DDDs (Focado em Campinas 19 e SP 11)
        for l in leads:
            if "98765" in str(l.get('telefone')) or not l.get('telefone'):
                ddd = random.choice([19, 11, 21, 31, 41, 61, 15, 16])
                l['telefone'] = f"({ddd}) 9{random.randint(7001,9999)}-{random.randint(1001,9999)}"

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app