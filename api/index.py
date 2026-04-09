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

        # COMANDO DE ALTO VOLUME E ASSERTIVIDADE DE INVENTÁRIO
        prompt = (
            f"EXECUÇÃO DE PROTOCOLO SNIPER EM: {url}\n"
            "OBJETIVO: Gerar 90 leads qualificados (30 Rank A+, 30 Rank B, 30 Rank C).\n"
            "INSTRUÇÃO DE INVENTÁRIO: Identifique os produtos/imóveis e seus preços reais no link. "
            "Combine leads de alto poder aquisitivo com os itens mais caros, e assim sucessivamente.\n\n"
            "REGRAS RÍGIDAS:\n"
            "1. ORDEM: Retorne o JSON estritamente na ordem: todos os A+, depois todos os B, depois todos os C.\n"
            "2. PRODUTO: Use o NOME REAL do item que está no site. Proibido ser genérico.\n"
            "3. SEM LIXO: Remova campos de 'estratégia' ou textos longos. Foque no dado técnico.\n"
            "4. MOMENTO: Filtre apenas pessoas com status 'Pronto para comprar' ou 'Decidindo hoje'.\n\n"
            "FORMATO JSON: {'leads': [{'nome': '...', 'cargo': '...', 'salario': '...', 'classe': '...', 'produto': '...', 'telefone': '...', 'social': '...'}]}"
        )

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um processador de dados comerciais de alta precisão. Sua saída é técnica, volumosa e 100% baseada no inventário do link."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(completion.choices[0].message.content).get("leads", [])

        # Persistência silenciosa no Supabase para seu controle
        for l in leads:
            try:
                supabase.table("leads_hiper_assertivos").insert({
                    "empresa_origem": url,
                    "nome_lead": l.get("nome"),
                    "telefone": l.get("telefone"),
                    "classe_social": f"{l.get('classe')} ({l.get('salario')})",
                    "produto_sugerido": l.get("produto")
                }).execute()
            except: pass

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app