import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Inicialização Blindada
GROQ_KEY = os.environ.get("GROQ_API_KEY")
S_URL = os.environ.get("SUPABASE_URL")
S_KEY = os.environ.get("SUPABASE_KEY")

client_groq = Groq(api_key=GROQ_KEY)
supabase = create_client(S_URL, S_KEY)

@app.route('/api/analisar', methods=['POST'])
def analisar():
    try:
        data = request.json
        url_alvo = data.get('url')
        
        if not url_alvo:
            return jsonify({"error": "URL Ausente"}), 400

        # 1. ANÁLISE RÁPIDA (Modelo 8b para não dar Timeout)
        prompt_dna = f"Analise o DNA comercial deste site e defina o público: {url_alvo}"
        mapeamento = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt_dna}],
            model="llama-3.1-8b-instant",
        )
        dna = mapeamento.choices[0].message.content

        # 2. EXTRAÇÃO DE LEADS (JSON Estruturado)
        prompt_leads = (
            f"Com base no DNA: {dna}, gere 5 leads de alta conversão. "
            "Retorne APENAS um objeto JSON exatamente assim: "
            "{'leads': [{'nome': '...', 'telefone': '...', 'rede_social': '...', 'classe': 'Alta', 'produto': '...', 'estagio': 'Quente', 'tatica': '...'}]}"
        )
        
        leads_raw = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um extrator de dados JSON."},
                      {"role": "user", "content": prompt_leads}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        # Converte a resposta para dicionário Python
        lista_leads = json.loads(leads_raw.choices[0].message.content).get("leads", [])

        # 3. GRAVAÇÃO NO SUPABASE (Usando a Service Role que você configurou)
        for l in lista_leads:
            try:
                supabase.table("leads_hiper_assertivos").insert({
                    "empresa_origem": url_alvo,
                    "setor_identificado": dna[:200],
                    "nome_lead": l.get("nome"),
                    "telefone": l.get("telefone"),
                    "rede_social": l.get("rede_social"),
                    "classe_social": l.get("classe"),
                    "produto_sugerido": l.get("produto"),
                    "estagio_compra": l.get("estagio"),
                    "tatica_abordagem": l.get("tatica")
                }).execute()
            except Exception as e:
                print(f"Erro ao inserir lead: {e}")

        return jsonify({"status": "sucesso", "dados": lista_leads})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()