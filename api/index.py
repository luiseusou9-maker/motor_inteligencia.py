# ... resto do seu código acima ...
        return jsonify({"status": "sucesso", "dados": leads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Remova o 'handler = app' se ele estiver dando erro, 
# mas se o vercel.json acima for usado, pode deixar apenas assim:
app = app