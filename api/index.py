from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api')
def handler():
    return jsonify({
        "status": "online",
        "projeto": "RITT Intelligence",
        "mensagem": "Motor aguardando configuracao das chaves."
    })

# Esse comando é importante para a Vercel entender o Flask
if __name__ == "__main__":
    app.run()