import googlemaps
import json

# Suas chaves de elite
GOOGLE_MAPS_KEY = "AIzaSyDpHmD-5MipOLNo9NaDW2om5JcMwe0r93k"
gmaps = googlemaps.Client(key=GOOGLE_MAPS_KEY)

def testar_mineracao(bairro, cidade):
    print(f"🦅 RITT INTEL: Iniciando busca em {bairro}...")
    
    # Busca as clínicas
    query = f'clínicas no {bairro}, {cidade}'
    busca = gmaps.places(query=query, language='pt-BR')
    resultados = busca.get('results', [])

    for lugar in resultados[:3]: # Testa apenas os 3 primeiros
        nome = lugar.get('name')
        endereco = lugar.get('formatted_address')
        print(f"\n✅ Achado: {nome}")
        print(f"📍 Endereço: {endereco}")

if __name__ == "__main__":
    # Quando você quiser testar outro lugar, é só mudar aqui:
    testar_mineracao("Cambuí", "Campinas")