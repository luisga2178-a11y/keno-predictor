import pandas as pd
import numpy as np
from collections import Counter
import datetime
import os
import requests
from bs4 import BeautifulSoup
import re

# ---------------------------------------------------------
# 1. CONFIGURACIÓN Y CARGA DE DATOS
# ---------------------------------------------------------
CSV_FILE = 'keno_consolidado_unico.csv'

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    print("Error: No se encontró el archivo base de datos keno_consolidado_unico.csv.")
    exit()

print(f"Sorteos históricos previos en base de datos: {len(df)}")

# ---------------------------------------------------------
# 2. MÓDULO DE SCRAPING (EXTRACCIÓN EN VIVO EN KENO3.COM.CO)
# ---------------------------------------------------------
def capturar_nuevos_sorteos():
    url = "https://www.keno3.com.co/results"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    
    nuevos = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Conectando a {url}... Estado HTTP: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            filas = soup.find_all(['tr', 'div'], class_=re.compile(r'result|draw|row|item', re.I))
            
            for fila in filas:
                texto_fila = fila.get_text(separator=' ')
                match_sorteo = re.search(r'\b(A\d{5})\b', texto_fila)
                if match_sorteo:
                    sorteo_id = match_sorteo.group(1)
                    
                    nums = [int(n) for n in re.findall(r'\b\d+\b', texto_fila)]
                    balotas = [n for n in nums if 1 <= n <= 80 and n != int(sorteo_id[1:])]
                    
                    balotas_unicas = []
                    for b in balotas:
                        if b not in balotas_unicas:
                            balotas_unicas.append(b)
                            
                    if len(balotas_unicas) >= 18:
                        balotas_20 = sorted(balotas_unicas[:20])
                        fecha_hoy = datetime.datetime.now().strftime("%d/%m/%Y")
                        hora_ahora = datetime.datetime.now().strftime("%H:%M")
                        
                        reg = {
                            'Sorteo': sorteo_id,
                            'Fecha': fecha_hoy,
                            'Hora': hora_ahora,
                            'Resultados': " ".join([f"{x:02d}" for x in balotas_20])
                        }
                        for i, b in enumerate(balotas_20):
                            reg[f'B{i+1}'] = b
                        nuevos.append(reg)
            print(f"🌐 Extracción web finalizada. Nuevos sorteos detectados: {len(nuevos)}")
        else:
            print(f"⚠️ La web respondió con estado HTTP {response.status_code}.")
    except Exception as e:
        print(f"⚠️ Error conectando a la web de Keno: {e}")
        
    return pd.DataFrame(nuevos)

# Ejecutar actualización web
df_nuevos = capturar_nuevos_sorteos()

if not df_nuevos.empty:
    df = pd.concat([df_nuevos, df]).drop_duplicates(subset=['Sorteo']).reset_index(drop=True)
    df.to_csv(CSV_FILE, index=False)
    print(f"✅ Base de datos actualizada con nuevos sorteos. Total registros: {len(df)}")
else:
    print("ℹ️ No se encontraron sorteos nuevos en esta corrida o ya están al día.")

# ---------------------------------------------------------
# 3. MODELO DE PREDICCIÓN (ALGORITMO DE SCORING)
# ---------------------------------------------------------
balota_cols = [f'B{i}' for i in range(1, 21)]
draws = df[balota_cols].values

N_RECIENTES = 50
recent_draws = draws[:N_RECIENTES]
freq_counter = Counter(recent_draws.flatten())

retardos = {}
for num in range(1, 81):
    count = 0
    for draw in draws:
        if num in draw:
            break
        count += 1
    retardos[num] = count

scores = {}
for num in range(1, 81):
    frec = freq_counter.get(num, 0)
    ausencia = retardos[num]
    scores[num] = (frec * 1.8) + (ausencia * 0.4)

top_numeros = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]
pronostico_final = sorted([num for num, score in top_numeros])

fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------
# 4. GENERACIÓN DE ARCHIVOS DE SALIDA
# ---------------------------------------------------------
with open('ultima_prediccion.txt', 'w', encoding='utf-8') as f:
    f.write(f"=== PRONÓSTICO AUTOMÁTICO DE KENO ===\n")
    f.write(f"Última actualización: {fecha_actual}\n")
    f.write(f"Sorteos analizados: {len(df)}\n\n")
    f.write(f"TOP 20 NÚMEROS RECOMENDADOS:\n")
    f.write(" ".join([f"[{n:02d}]" for n in pronostico_final]))
    f.write("\n")

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predictor de Keno (Live)</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f6f9; text-align: center; padding: 20px; }}
        .card {{ background: white; max-width: 600px; margin: 0 auto; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a365d; margin-bottom: 5px; }}
        .sub {{ color: #718096; font-size: 14px; margin-bottom: 25px; }}
        .grid {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 20px; }}
        .ball {{ background: #2b6cb0; color: white; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🎯 Pronóstico Automático Keno</h1>
        <div class="sub">Conectado a Keno3 | Actualizado: {fecha_actual} | Base: {len(df)} sorteos</div>
        <h3>Top 20 Números Sugeridos:</h3>
        <div class="grid">
            {"".join([f'<div class="ball">{n:02d}</div>' for n in pronostico_final])}
        </div>
    </div>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Predicción generada con éxito el {fecha_actual}.")
print(f"Top 20 sugerido: {pronostico_final}")
