import pandas as pd
import numpy as np

archivo_entrada = '/Users/*****/Desktop/data para limpiar .csv'
archivo_salida = '/Users/*****/Desktop/reporte_tomadas.csv'

try:
    print("Limpiando y dando formato a la tabla...")
    
    # 1. Leer el archivo saltando las primeras 5 filas de encabezados basura
    df = pd.read_csv(archivo_entrada, skiprows=5, low_memory=False)
    
    # Limpiar espacios en los nombres de las columnas
    df.columns = df.columns.str.strip()

    # 2. Detectar las fechas en la columna 'Period' (formato YYYY-MM-DD)
    es_fecha = df['Period'].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}')
    
    # 3. Crear la columna 'Date' y rellenar las fechas hacia abajo
    df['Date'] = np.where(es_fecha, df['Period'], np.nan)
    df['Date'] = df['Date'].ffill()

    # 4. Limpiar filas que no necesitamos 
    df = df[~es_fecha] 
    df = df[~df['Period'].astype(str).str.contains('Total', na=False, case=False)]
    df = df.dropna(subset=['Period']) # Eliminar filas donde el Period esté vacío

    # 5. Dar formato a la fecha y calcular el día de la semana ('Day')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day'] = df['Date'].dt.day_name()

    # 6. Ordenar las fechas de la más nueva a la más vieja
    df = df.sort_values(by='Date', ascending=False)
    
    # Convertir la fecha de vuelta a texto (YYYY-MM-DD) 
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

    # 7. Seleccionar solo las columnas deseadas 
    columnas_deseadas = ['Date', 'Day', 'Period', 'Taken']
    df_final = df[columnas_deseadas].copy()

    # 8. Convertir 'Taken' a formato numérico con decimal (ej. 4.0, 0.0)
    df_final['Taken'] = pd.to_numeric(df_final['Taken'], errors='coerce').fillna(0).astype(float)

    # 9. Guardar el archivo limpio y formateado
    df_final.to_csv(archivo_salida, index=False)
    print("¡Listo! Tu archivo 'reporte_tomadas.csv' ahora tiene el formato idéntico al de tu imagen.")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo en la ruta:\n{archivo_entrada}")
except Exception as e:
    print(f"Ocurrió un error: {e}")