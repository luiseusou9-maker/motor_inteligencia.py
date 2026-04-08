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

        # PROMPT DE ALTO IMPACTO - FOCO EM CLASSE A+ E ENCAIXE DE PRODUTO
        prompt_mestre = (
            f"Analise o site {url}. Identifique os produtos/imóveis de maior valor.\n"
            "Gere 10 leads REAIS de altíssimo padrão (CLASSE A+).\n"
            "REGRAS OBRIGATÓRIAS:\n"
            "1. IDIOMA: Português Brasil.\n"
            "2. PERFIL: Apenas Donos de Empresas, CEOs, Médicos e Investidores.\n"
            "3. SALÁRIO: Estime valores acima de R$ 50.000,00.\n"
            "4. PRODUTO: No campo 'produto', diga exatamente qual item do site esse lead deve comprar.\n"
            "5. MOMENTO: Identifique quem está em 'Decisão Imediata'.\n"
            "Retorne APENAS JSON:\n"
            "{{'leads': [{{'nome': '...', 'cargo': '...', 'salario': '...', 'momento': '...', 'telefone': '...', 'classe': 'A+', 'produto': '...', 'tatica': '...'}}]}}"
        )

        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um Head de Inteligência Comercial focado em Mercado de Luxo."},
                      {"role": "user", "content": prompt_mestre}],
            model="llama-3.1-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(res.choices[0].message.content).get("leads", [])

        # Salva no banco de dados
        for l in leads:
            try:
                supabase.table("leads_hiper_assertivos").insert({
                    "empresa_origem": url,
                    "nome_lead": l.get("nome"),
                    "telefone": l.get("telefone"),
                    "classe_social": f"{l.get('classe')} ({l.get('salario')})",
                    "produto_sugerido": f"{l.get('produto')} | {l.get('cargo')}",
                    "estagio_compra": l.get("momento"),
                    "tatica_abordagem": l.get("tatica")
                }).execute()
            except: pass

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app