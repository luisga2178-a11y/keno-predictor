def capturar_sorteos_api():
    api_url = "https://backend-keno.gana-web.com/api/keno/draws"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Origin': 'https://www.keno3.com.co',
        'Referer': 'https://www.keno3.com.co/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site'
    }
    
    nuevos = []
    try:
        response = requests.get(api_url, headers=headers, timeout=12)
        print(f"Conectando a API oficial ({api_url})... Estado HTTP: {response.status_code}")
        
        if response.status_code == 200:
            datos_json = response.json()
            items = datos_json if isinstance(datos_json, list) else datos_json.get('data', datos_json.get('draws', datos_json.get('results', [])))
            
            for item in items:
                sorteo_raw = item.get('drawNumber', item.get('draw', item.get('id', item.get('sorteo', ''))))
                sorteo_id = str(sorteo_raw)
                if sorteo_id and not sorteo_id.startswith('A'):
                    sorteo_id = f"A{sorteo_id}"
                
                balotas = item.get('winningNumbers', item.get('numbers', item.get('results', item.get('balotas', []))))
                
                if isinstance(balotas, str):
                    balotas = [int(n) for n in balotas.replace(',', ' ').split() if n.isdigit()]
                
                if sorteo_id and len(balotas) >= 18:
                    balotas_20 = sorted([int(b) for b in balotas[:20]])
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
                    
            print(f"✅ Sorteos extraídos correctamente desde la API: {len(nuevos)}")
        else:
            print(f"⚠️ La API respondió con estado HTTP: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error al consultar la API: {e}")
        
    return pd.DataFrame(nuevos)
