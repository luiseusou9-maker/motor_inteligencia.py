import os
from groq import Groq
import requests

# Configuração da Glock (Groq)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analisar_empresa(url):
    """Analisa o site para entender o setor e o público-alvo"""
    # Aqui simulamos a leitura do site para a IA definir o perfil
    prompt = f"Analise este link: {url}. Identifique os produtos e o perfil do cliente ideal (Poder aquisitivo, interesses, urgência)."
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "system", "content": "Você é um analista de vendas experiente."},
                  {"role": "user", "content": prompt}],
        model="llama3-70b-8192",
    )
    return chat_completion.choices[0].message.content

def capturar_hiper_leads(perfil_analisado):
    """Busca leads no Maps e filtra pela inteligência da Glock"""
    # A lógica aqui cruza o perfil com a busca geográfica
    prompt_leads = f"Com base neste perfil: {perfil_analisado}, gere uma lista de leads prioritários com Nome, Telefone e Por que são potenciais."
    
    # Simulação da busca rápida da Glock
    chat_completion = client.chat.completions.create(
        messages=[{"role": "system", "content": "Gere uma lista de leads assertivos (Nome, Tel, Score de 1 a 10)."},
                  {"role": "user", "content": prompt_leads}],
        model="llama3-70b-8192",
    )
    return chat_completion.choices[0].message.content