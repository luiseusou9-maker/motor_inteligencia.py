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

        # PROTOCOLO DE DUAS ETAPAS: SCAN DE PRODUTO + CRUZAMENTO DE LEADS
        prompt_operacional = (
            f"DIRETRIZ OBRIGATÓRIA PARA O AGENTE:\n"
            f"1. ACESSE O LINK: {url} e identifique EXATAMENTE o que é vendido (Imóveis, Carros, etc).\n"
            f"2. MAPEIE O INVENTÁRIO: Liste mentalmente os 3 produtos mais caros, os médios e os de entrada.\n"
            f"3. GERAÇÃO DE LEADS (30 LEADS): Gere 10 leads para cada classe (A+, B, C).\n\n"
            "CRITÉRIOS DE ASSERTIVIDADE REAIS:\n"
            "- LEADS CLASSE A+: Somente CEOs ou Médicos com renda > 80k para os produtos de luxo do site.\n"
            "- LEADS CLASSE B: Profissionais liberais com renda 15k-35k para os produtos médios do site.\n"
            "- LEADS CLASSE C: Assalariados ou autônomos com renda 5k-12k para os itens de entrada do site.\n\n"
            "REGRAS DE OURO:\n"
            "- Proibido oferecer algo que não tem no site (Ex: Se for site de casa, não ofereça carro).\n"
            "- O campo 'PRODUTO' deve citar o nome/modelo/bairro real encontrado no link.\n"
            "- O campo 'TATICA' deve ser um script de abordagem profissional, não um comentário pessoal.\n\n"
            "Retorne JSON: {'leads': [{'nome': '...', 'cargo': '...', 'salario': '...', 'momento': '...', 'telefone': '...', 'classe': '...', 'produto': '...', 'social': '...', 'tatica': '...'}]}"
        )

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um Especialista em Inteligência de Inventário. Sua missão é ler o site e encontrar compradores reais para os produtos específicos que estão na vitrine."},
                {"role": "user", "content": prompt_operacional}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(completion.choices[0].message.content).get("leads", [])

        # Persistência no Supabase
        for l in leads:
            try:
                supabase.table("leads_hiper_assertivos").insert({
                    "empresa_origem": url,
                    "nome_lead": l.get("nome"),
                    "telefone": l.get("telefone"),
                    "classe_social": f"{l.get('classe')} ({l.get('salario')})",
                    "produto_sugerido": l.get("produto"),
                    "estagio_compra": l.get("momento"),
                    "tatica_abordagem": l.get("social")
                }).execute()
            except: pass

        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app