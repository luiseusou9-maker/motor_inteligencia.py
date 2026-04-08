import os
from flask import Flask, jsonify
from flask_cors import CORS
import googlemaps
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# PUXANDO AS VARIÁVEIS DE AMBIENTE DA VERCEL (SEGURO E PROFISSIONAL)
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializa os clientes usando as variáveis acima
gmaps = googlemaps.Client(key=GOOGLE_MAPS_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)