import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# Configurações de Ambiente (Vercel)
GROQ_KEY = os.environ.get("GROQ_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inicialização das Ferramentas
groq_client = Groq(api_key=GROQ_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    return "Motor RITT Inteligência - Glock & Supabase Ativos"

@app.route('/api/analisar', methods=['POST'])
def analisar_e_rastrear():
    data = request.json
    url_cliente = data.get('url')

    if not url_cliente:
        return jsonify({"error": "Link não fornecido"}), 400

    try:
        # 1. INTELIGÊNCIA: Glock analisa o site e define o alvo
        analise_perfil = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um Analista de Inteligência de Vendas. Identifique o produto e o perfil de cliente do site."},
                {"role": "user", "content": f"Mapeie os setores deste link: {url_cliente}"}
            ],
            model="llama3-8b-8192",
        )
        setor = analise_perfil.choices[0].message.content

        # 2. CAPTURA: Glock gera os leads assertivos em formato JSON para o sistema ler
        gerar_leads = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Gere uma lista de 5 leads HIPER ASSERTIVOS em formato JSON puro. Use os campos: nome, telefone, prioridade, score, tatica."},
                {"role": "user", "content": f"Baseado no setor {setor}, traga leads potenciais."}
            ],
            model="llama3-70b-8192",
            response_format={"type": "json_object"} # Força a Glock a mandar JSON limpo
        )
        
        leads_json = json.loads(gerar_leads.choices[0].message.content)
        leads_lista = leads_json.get("leads", [])

        # 3. O SALVE: Gravando na tabela fortificada do Supabase
        for lead in leads_lista:
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url_cliente,
                "setor_identificado": setor[:200], # Limita o texto para não estourar
                "nome_lead": lead.get("nome"),
                "telefone": lead.get("telefone"),
                "prioridade": lead.get("prioridade"),
                "score_assertividade": lead.get("score"),
                "tatica_abordagem": lead.get("tatica")
            }).execute()

        return jsonify({
            "status": "Máquina Rodando",
            "setor": setor,
            "leads_capturados": len(leads_lista),
            "dados": leads_lista
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)