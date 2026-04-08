import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Adicionamos um log para ver se o Python está carregando os módulos
try:
    from groq import Groq
    from supabase import create_client
except ImportError as e:
    print(f"ERRO DE IMPORTAÇÃO: {e}")

app = Flask(__name__)
CORS(app)

@app.route('/api/analisar', methods=['POST'])
def analisar():
    try:
        # 1. Checagem de Variáveis
        groq_key = os.environ.get("GROQ_API_KEY")
        s_url = os.environ.get("SUPABASE_URL")
        s_key = os.environ.get("SUPABASE_KEY")

        if not groq_key or not s_url or not s_key:
            return jsonify({"error": "Configurações incompletas na Vercel"}), 500

        # O motor começa aqui
        # ... (restante do código de análise) ...
        
        return jsonify({"status": "sucesso", "dados": []})

    except Exception as e:
        # O segredo profissional: retornar o erro real para o console do navegador
        print(f"DEBUG: {str(e)}")
        return jsonify({"error": str(e), "trace": str(sys.exc_info())}), 500