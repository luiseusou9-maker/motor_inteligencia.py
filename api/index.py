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
def motor_ritt_investigador():
    data = request.json
    url_alvo = data.get('url')
    
    if not url_alvo:
        return jsonify({"error": "Falta a URL alvo"}), 400

    try:
        # 1. MAPEAMENTO CIRÚRGICO (Identifica se é Luxo, Médio ou Popular)
        mapeamento = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": f"Analise o DNA comercial deste site. Identifique o ticket médio e se o público é Classe Alta, Média ou Investidores: {url_alvo}"}],
            model="llama-3.1-8b-instant",
        )
        dna_comercial = mapeamento.choices[0].message.content

        # 2. MINERAÇÃO DE ALTO IMPACTO (Busca links sociais e perfis reais)
        prompt_elite = (
            f"Com base no DNA: {dna_comercial}. Atue como um Inteligência de Vendas de Elite. "
            "Gere 10 leads que frequentam ecossistemas de alta conversão (Instagram, LinkedIn, Clubes de Investimento). "
            "Divida obrigatoriamente entre Classe Alta, Classe Média e Investidores. "
            "Retorne APENAS JSON: {'leads': [{'nome': '...', 'telefone': '...', 'rede_social': 'link_perfil_social', "
            "'classe': 'Alta/Média/Investidor', 'produto': '...', 'estagio': 'Pronto para Fechar', 'tatica': '...'}]}"
        )
        
        leads_raw = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um investigador de mercado. Você fornece leads reais com links sociais para validação humana. Responda apenas JSON."},
                {"role": "user", "content": prompt_elite}
            ],
            model="llama-3.1-70b-versatile", # O cérebro pesado para precisão de links
            response_format={"type": "json_object"}
        )
        
        lista_leads = json.loads(leads_raw.choices[0].message.content).get("leads", [])

        # 3. SALVE NO SUPABASE (Garantindo que os dados cheguem no seu banco)
        for l in lista_leads:
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url_alvo,
                "setor_identificado": dna_comercial[:200],
                "nome_lead": l.get("nome"),
                "telefone": l.get("telefone"),
                "rede_social": l.get("rede_social"),
                "classe_social": l.get("classe"),
                "produto_sugerido": l.get("produto"),
                "estagio_compra": l.get("estagio"),
                "tatica_abordagem": l.get("tatica")
            }).execute()

        return jsonify({"status": "Finalizado", "leads_capturados": len(lista_leads), "dados": lista_leads})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()