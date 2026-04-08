import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from supabase import create_client

# 1. SETUP INICIAL
app = Flask(__name__)
CORS(app)

# Chaves de Acesso
GROQ_KEY = os.environ.get("GROQ_API_KEY")
S_URL = os.environ.get("SUPABASE_URL")
S_KEY = os.environ.get("SUPABASE_KEY")

client_groq = Groq(api_key=GROQ_KEY)
supabase = create_client(S_URL, S_KEY)

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        url_alvo = data.get('url')
        
        # --- CAMADA 1: O CÉREBRO APRENDIZ (ANÁLISE DE MERCADO) ---
        # Instruímos a IA a ser minuciosa e observar tendências reais
        prompt_deep_scan = (
            f"Aja como um Analista de Mercado de Luxo e Real Estate. Analise a URL {url_alvo}.\n"
            "MISSÃO: Identifique o DNA do negócio. Se for imobiliária, foque em: Mansões, Terrenos, Condomínios.\n"
            "Não aceite resultados genéricos. Observe o nível de sofisticação do site."
        )
        
        recon_res = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt_deep_scan}],
            model="llama-3.1-8b-instant"
        )
        contexto_mercado = recon_res.choices[0].message.content

        # --- CAMADA 2: RASTREIO DE ALTA ASSERTIVIDADE (O 70B ENTRA AQUI) ---
        prompt_leads = (
            f"Contexto do Alvo: {contexto_mercado}.\n"
            "Com base nessa análise, rastreie 5 leads Reais (Persona Business).\n"
            "REGRAS RÍGIDAS:\n"
            "1. Se o ticket for ALTO (Mansões), os leads devem ser CLASSE A (Investidores/Diretores).\n"
            "2. Proibido fones de ouvido, tecnologia barata ou software genérico.\n"
            "3. Use DDD 19 para região de Campinas ou conforme o site indicar.\n"
            "4. A Tática de Abordagem deve ser de Nível VIP.\n"
            "Retorne APENAS JSON: {'leads': [{'nome': '...', 'telefone': '...', 'classe': 'A', 'produto': 'Mansão/Terreno Específico', 'tatica': '...'}]}"
        )

        leads_raw = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é o NEURAL COMMANDER. Um caçador de leads de elite que aprende com cada varredura. Foque no mercado de alto padrão."},
                {"role": "user", "content": prompt_leads}
            ],
            model="llama-3.1-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        leads_data = json.loads(leads_raw.choices[0].message.content)
        lista_leads = leads_data.get("leads", [])

        # --- CAMADA 3: REGISTRO NO SUPABASE ---
        for l in lista_leads:
            nome_limpo = l.get('nome').replace(' ', '+')
            # Link de busca inteligente no LinkedIn/Google
            link_investigacao = f"https://www.google.com/search?q=site:linkedin.com/in/+%22{nome_limpo}%22"
            
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url_alvo,
                "setor_identificado": contexto_mercado[:300],
                "nome_lead": l.get("nome"),
                "telefone": l.get("telefone"),
                "rede_social": link_investigacao,
                "classe_social": l.get("classe"),
                "produto_sugerido": l.get("produto"),
                "estagio_compra": "Lead Qualificado High-Ticket",
                "tatica_abordagem": l.get("tatica")
            }).execute()

        return jsonify({"status": "sucesso", "dados": lista_leads})

    except Exception as e:
        print(f"ERRO: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Handler para Vercel
handler = app