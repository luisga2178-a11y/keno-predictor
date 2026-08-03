import pandas as pd
import numpy as np
from collections import Counter
import datetime
import os

# ---------------------------------------------------------
# 1. CONFIGURACIÓN Y CARGA DE DATOS
# ---------------------------------------------------------
CSV_FILE = 'keno_consolidado_unico.csv'

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    print("Error: No se encontró el archivo base de datos keno_consolidado_unico.csv.")
    exit()

print(f"Sorteos históricos en base de datos: {len(df)}")

# ---------------------------------------------------------
# 2. MODELO DE PREDICCIÓN (ALGORITMO DE SCORING)
# ---------------------------------------------------------
balota_cols = [f'B{i}' for i in range(1, 21)]
draws = df[balota_cols].values

# A) Frecuencia Reciente (Últimos 50 sorteos)
N_RECIENTES = 50
recent_draws = draws[:N_RECIENTES]
freq_counter = Counter(recent_draws.flatten())

# B) Cálculo de Retardo (Sorteos sin salir)
retardos = {}
for num in range(1, 81):
    count = 0
    for draw in draws:
        if num in draw:
            break
        count += 1
    retardos[num] = count

# C) Puntaje Ponderado (Tendencia + Atraso)
scores = {}
for num in range(1, 81):
    frec = freq_counter.get(num, 0)
    ausencia = retardos[num]
    scores[num] = (frec * 1.8) + (ausencia * 0.4)

# D) Top 20 Números Sugeridos
top_numeros = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]
pronostico_final = sorted([num for num, score in top_numeros])

fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------
# 3. GENERACIÓN DE ARCHIVOS DE SALIDA
# ---------------------------------------------------------

# Salida 1: Archivo de texto plano (ultima_prediccion.txt)
with open('ultima_prediccion.txt', 'w', encoding='utf-8') as f:
    f.write(f"=== PRONÓSTICO AUTOMÁTICO DE KENO ===\n")
    f.write(f"Última actualización: {fecha_actual}\n")
    f.write(f"Sorteos analizados: {len(df)}\n\n")
    f.write(f"TOP 20 NÚMEROS RECOMENDADOS:\n")
    f.write(" ".join([f"[{n:02d}]" for n in pronostico_final]))
    f.write("\n")

# Salida 2: Página Web HTML interactiva (index.html para GitHub Pages)
html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predictor de Keno</title>
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
        <div class="sub">Actualizado: {fecha_actual} | Base: {len(df)} sorteos</div>
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
