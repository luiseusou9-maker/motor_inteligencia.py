def motor_de_ataque_global(url):
    # Ajustamos o prompt para ser cirúrgico com a nossa tabela leads_auditoria
    prompt_unico = (
        f"ALVO: {url}. MISSÃO: DEEP SCAN DE CATÁLOGO.\n"
        "1. Identifique o estoque imobiliário (Lugar, Endereço e Valor).\n"
        "2. Gere 30 leads de ALTA INTENCIONALIDADE (Brasil todo).\n"
        "REGRAS DE OURO:\n"
        "- Rank A+: Renda R$ 120k+ (Sócios/Investidores).\n"
        "- Rank B: Renda R$ 30k-60k (Executivos).\n"
        "- Rank C/D: Renda compatível com Lotes/Casas.\n"
        "SAÍDA OBRIGATÓRIA JSON COM AS CHAVES DA TABELA: "
        "['nome', 'cargo', 'renda', 'classe', 'reside_atualmente', 'produto_alvo', 'endereco_imovel', 'perfil_comportamental', 'telefone', 'match_score']"
    )

    # O 8b é o pé no chão, excelente escolha para não estourar o limite de tempo
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Você é um Corretor Digital Sniper. Sua saída é APENAS JSON puro e direto."},
            {"role": "user", "content": prompt_unico}
        ],
        model="llama-3.1-8b-instant",
        temperature=0.4, # Garante que os nomes e perfis não sejam repetidos
        response_format={"type": "json_object"}
    )
    
    return chat_completion.choices[0].message.content