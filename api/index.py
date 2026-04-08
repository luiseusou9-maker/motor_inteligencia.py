# --- PROTOCOLO NEURAL COMMANDER: PESQUISA PROFUNDA ---

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    if request.method == 'OPTIONS': return '', 200
    
    try:
        data = request.json
        url_alvo = data.get('url')
        
        # 1. CAMADA DE RECONHECIMENTO (Sem pressa)
        prompt_recon = (
            f"FASE 1: RECONHECIMENTO MINUCIOSO.\n"
            f"Analise o site {url_alvo} como se fosse um comprador real.\n"
            "Liste os 3 produtos/serviços de maior valor e os 3 de entrada.\n"
            "Defina o ticket médio e a região geográfica exata de atuação."
        )
        recon_res = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt_recon}],
            model="llama-3.1-8b-instant" # Rapidez no reconhecimento
        )
        contexto = recon_res.choices[0].message.content

        # 2. CAMADA DE INTENÇÃO DE BUSCA (A "Mente" do Cliente)
        # Aqui a gente foca em quem está pesquisando ativamente (Rede de Pesquisa)
        prompt_rastreio = (
            f"FASE 2: RASTREIO DE INTENÇÃO.\n"
            f"Contexto do Site: {contexto}.\n"
            "Sua missão agora é rastrear 5 leads que estão na REDE DE PESQUISA (Google/Bing) "
            "procurando ativamente por esses produtos AGORA.\n"
            "REGRAS DE OURO:\n"
            "1. Pessoas com intenção real de compra (Search Intent).\n"
            "2. Encaixe cada lead em uma classe (A, B ou C) baseada no produto que ele busca.\n"
            "3. Use nomes brasileiros reais e DDDs compatíveis com a região do site.\n"
            "4. A Tática de Abordagem deve ser baseada na 'dor' de quem está pesquisando.\n"
            "Retorne APENAS JSON: {'leads': [{'nome': '...', 'telefone': '...', 'classe': '...', 'produto': '...', 'tatica': '...'}]}"
        )

        leads_raw = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um Analista de Big Data focado em Intenção de Compra. Seja minucioso e realista."},
                      {"role": "user", "content": prompt_rastreio}],
            model="llama-3.1-70b-versatile", # AQUI USAMOS O CÉREBRO MAIOR PARA A ANÁLISE FINAL
            response_format={"type": "json_object"}
        )
        
        lista_leads = json.loads(leads_raw.choices[0].message.content).get("leads", [])

        # 3. SINCRONIZAÇÃO NO SUPABASE
        for l in lista_leads:
            # Geramos link de busca focado em 'Decision Makers' (Tomadores de Decisão)
            link_social = f"https://www.google.com/search?q=site:linkedin.com/in/+%22{l.get('nome').replace(' ', '+')}%22"
            
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url_alvo,
                "setor_identificado": contexto[:300],
                "nome_lead": l.get("nome"),
                "telefone": l.get("telefone"),
                "rede_social": link_social,
                "classe_social": l.get("classe"),
                "produto_sugerido": l.get("produto"),
                "estagio_compra": "Intenção de Busca Ativa",
                "tatica_abordagem": l.get("tatica")
            }).execute()

        return jsonify({"status": "sucesso", "dados": lista_leads})

    except Exception as e:
        return jsonify({"error": str(e)}), 500