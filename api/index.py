import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Chaves de Comando (Vercel Environment Variables)
GROQ_KEY = os.environ.get("GROQ_API_KEY")
S_URL = os.environ.get("SUPABASE_URL")
S_KEY = os.environ.get("SUPABASE_KEY")

client_groq = Groq(api_key=GROQ_KEY)
supabase = create_client(S_URL, S_KEY)

@app.route('/api/analisar', methods=['POST'])
def rota_neural_commander():
    data = request.json
    url_alvo = data.get('url')
    
    if not url_alvo:
        return jsonify({"error": "Falta a URL alvo"}), 400

    try:
        # 1. ANÁLISE DE DNA (AIA de reconhecimento rápido)
        mapeamento = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": f"Analise este site e defina o público e ticket médio: {url_alvo}"}],
            model="llama-3.1-8b-instant",
        )
        dna_comercial = mapeamento.choices[0].message.content

        # 2. GERAÇÃO DE ALVOS (AIA de Profundidade)
        prompt_elite = (
            f"DNA: {dna_comercial}. Atue como Inteligência Neural de Vendas. "
            "Gere 10 leads de alta performance com links sociais. "
            "Retorne APENAS JSON: {'leads': [{'nome': '...', 'telefone': '...', 'rede_social': '...', "
            "'classe': 'Alta/Média', 'produto': '...', 'estagio': 'Morno/Quente', 'tatica': '...'}]}"
        )
        
        leads_raw = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é o NEURAL COMMANDER. Responda apenas JSON."},
                {"role": "user", "content": prompt_elite}
            ],
            model="llama-3.1-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        lista_leads = json.loads(leads_raw.choices[0].message.content).get("leads", [])

        # 3. CONEXÃO COM O BANCO (Garantindo o salvamento)
        for l in lista_leads:
            try:
                supabase.table("leads_hiper_assertivos").insert({
                    "empresa_origem": url_alvo,
                    "setor_identificado": dna_comercial[:250],
                    "nome_lead": l.get("nome"),
                    "telefone": l.get("telefone"),
                    "rede_social": l.get("rede_social"),
                    "classe_social": l.get("classe"),
                    "produto_sugerido": l.get("produto"),
                    "estagio_compra": l.get("estagio"),
                    "tatica_abordagem": l.get("tatica")
                }).execute()
            except Exception:
                continue # Se um falhar, não mata a lista

        return jsonify({"status": "Finalizado", "dados": lista_leads})

    except Exception as e:
        return jsonify({"error": "Falha no conector: " + str(e)}), 500

if __name__ == "__main__":
    app.run()