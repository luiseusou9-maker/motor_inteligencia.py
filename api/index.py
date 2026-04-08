import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Inicialização com verificação de erro
try:
    client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
except Exception as e:
    print(f"Erro na inicialização: {e}")

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({"error": "URL faltando"}), 400
            
        url_alvo = data.get('url')

        # ÚNICO PROMPT - Direto e sem enrolação para não dar timeout
        prompt = (
            f"Analise o site {url_alvo}. Identifique o nicho (Imobiliário/Luxo). "
            "Gere 5 leads reais (Investidores/Diretores) para este negócio. "
            "Se for em Campinas, use DDD 19. Foque em MANSÕES e TERRENOS. "
            "Responda APENAS JSON: {'leads': [{'nome': 'Nome', 'telefone': '19...', 'classe': 'A', 'produto': 'Mansão', 'tatica': 'VIP'}]}"
        )

        completion = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": "Analista comercial de alto padrão. Responda apenas JSON."},
                      {"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        leads = json.loads(completion.choices[0].message.content).get("leads", [])

        # Salva no banco (Silencioso)
        for l in leads:
            try:
                supabase.table("leads_hiper_assertivos").insert({
                    "empresa_origem": url_alvo,
                    "nome_lead": l.get("nome"),
                    "telefone": l.get("telefone"),
                    "classe_social": l.get("classe"),
                    "produto_sugerido": l.get("produto"),
                    "tatica_abordagem": l.get("tatica")
                }).execute()
            except:
                pass

        return jsonify({"status": "sucesso", "dados": leads})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app