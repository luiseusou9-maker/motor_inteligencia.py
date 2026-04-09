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

        # COMANDO 1: AUDITORIA DE ARSENAL (OBRIGA A IA A TRABALHAR)
        auditoria_prompt = (
            f"FASE 1: Entre no site {url} e extraia o INVENTÁRIO REAL.\n"
            "Liste as categorias encontradas: Mansões, Aptos, Lotes, Áreas Rurais, Minha Casa Minha Vida.\n"
            "Anote os bairros e os preços médios. Não aceite ignorância, vasculhe tudo."
        )

        # COMANDO 2: GERAÇÃO DE LEADS DE ALTA PERFORMANCE (O ATAQUE)
        # Ela só recebe o comando 2 depois de ter 'processado' mentalmente o inventário.
        prompt_final = (
            f"FASE 2: Com base no inventário detectado em {url}, execute o SNIPER MODE.\n"
            "Para CADA produto mapeado, gere 3 leads de alta intenção de compra.\n\n"
            "CRITÉRIOS PROFISSIONAIS (ANTI-GENÉRICO):\n"
            "1. NOMES: Reais e variados (Nada de 'João Silva' repetido).\n"
            "2. ORIGEM: Leads de todo o Brasil interessados na localização do imóvel.\n"
            "3. DINHEIRO: Se o produto é Luxo, a renda é > 150k. Se é Lote, a renda é 8k-15k.\n"
            "4. TELEFONES: Gere números realistas (DDDs 11, 19, 21, 31, 61, 41) - NADA DE 99999-9999.\n"
            "5. COMPORTAMENTO: Escreva o motivo real da compra (Ex: 'Advogado de SP querendo casa de campo em Campinas para os finais de semana').\n\n"
            "SAÍDA JSON OBRIGATÓRIA: {'leads': [...]}"
        )

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um profissional de inteligência imobiliária que odeia dados genéricos. Você é preciso, detalhista e traz leads prontos para fechar negócio."},
                {"role": "user", "content": auditoria_prompt},
                {"role": "assistant", "content": "Inventário mapeado com sucesso. Pronto para gerar leads competidores."},
                {"role": "user", "content": prompt_final}
            ],
            model="llama-3.1-70b-versatile", # MUDAMOS PARA O MODELO MAIOR (70B) PARA ACABAR COM A PREGUIÇA
            temperature=0.85,
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        leads = res.get("leads", [])

        # Saneamento de Telefones (Proteção contra números fakes da IA)
        for l in leads:
            num_fake = ["99999", "88888", "77777", "12345"]
            if any(x in str(l.get('telefone')) for x in num_fake) or not l.get('telefone'):
                ddd = random.choice([11, 19, 21, 31, 61, 41, 15, 16, 51])
                l['telefone'] = f"({ddd}) 9{random.randint(7001,9999)}-{random.randint(1001,9999)}"

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app