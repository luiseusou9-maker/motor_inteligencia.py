@app.route('/api/analisar', methods=['POST'])
def analisar():
    try:
        data = request.json
        url_alvo = data.get('url')
        
        # 1. CAMADA DE RECONHECIMENTO (A IA "entra" na loja/site)
        prompt_scan = (
            f"Aja como um Perito Comercial. Analise a URL {url_alvo} e extraia: "
            "1. O nicho exato (Imobiliário, Tech, Varejo, etc.). "
            "2. Localização da operação (Cidade/Estado ou Global). "
            "3. O perfil financeiro do cliente (Classe A, B, C ou D)."
        )
        
        reconhecimento = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt_scan}],
            model="llama-3.1-8b-instant"
        ).choices[0].message.content

        # 2. CAMADA DE RASTREIO DE ALVOS (Busca por personas reais)
        prompt_rastreio = (
            f"Com base no reconhecimento: {reconhecimento}. "
            f"Identifique 5 leads que possuem o DNA de compra para {url_alvo}. "
            "IMPORTANTE: Se o negócio for local (ex: Campinas), use nomes e DDDs (19) reais da região. "
            "Cruze dados de possíveis perfis de redes sociais profissionais. "
            "Responda APENAS JSON: "
            "{'leads': [{'nome': 'Nome Completo Real', 'telefone': '+55 (DDD) ...', 'classe': 'A', 'produto': 'Produto específico do site', 'tatica': 'Estratégia personalizada'}]}"
        )

        leads_raw = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um rastreador de leads de elite. Proibido sugerir produtos genéricos."},
                      {"role": "user", "content": prompt_rastreio}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        lista_leads = json.loads(leads_raw.choices[0].message.content).get("leads", [])

        # 3. GRAVAÇÃO NO SUPABASE (Sincronização imediata)
        for l in lista_leads:
            supabase.table("leads_hiper_assertivos").insert({
                "empresa_origem": url_alvo,
                "setor_identificado": reconhecimento[:300],
                "nome_lead": l.get("nome"),
                "telefone": l.get("telefone"),
                "rede_social": f"https://www.instagram.com/{l.get('nome').lower().replace(' ', '')}",
                "classe_social": l.get("classe"),
                "produto_sugerido": l.get("produto"),
                "estagio_compra": "Análise de Potencial",
                "tatica_abordagem": l.get("tatica")
            }).execute()

        return jsonify({"status": "sucesso", "dados": lista_leads})

    except Exception as e:
        return jsonify({"error": str(e)}), 500