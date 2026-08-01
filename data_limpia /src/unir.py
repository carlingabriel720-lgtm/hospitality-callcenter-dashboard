import pandas as pd

# Rutas actualizadas a tu nueva carpeta 'data limpia'
archivo_1 = '/Users/*****/Desktop/data limpia /data_limpia.csv'
archivo_2 = '/Users/*****/Desktop/data limpia /reporte_tomadas.csv'

# Guardaremos el archivo final en esa misma carpeta
archivo_salida = '/Users/*****/Desktop/data limpia /data_unificada_final.csv'

try:
    print("Cargando las dos tablas...")
    df1 = pd.read_csv(archivo_1)
    df2 = pd.read_csv(archivo_2)

    # Asegurarnos de que ambas tablas tengan solo las 4 columnas
    columnas = ['Date', 'Day', 'Period', 'Taken']
    df1 = df1[columnas]
    df2 = df2[columnas]

    print("Uniendo las tablas...")
    # Unir una tabla debajo de la otra
    df_unido = pd.concat([df1, df2], ignore_index=True)

    print(f"Filas antes de limpiar duplicados: {len(df_unido)}")

    # ELIMINAR DUPLICADOS: Deja solo una copia de las filas que son idénticas
    df_unido = df_unido.drop_duplicates()

    print(f"Filas después de limpiar duplicados: {len(df_unido)}")

    # Asegurar formato numérico para 'Taken' con un decimal (ej. 4.0)
    df_unido['Taken'] = pd.to_numeric(df_unido['Taken'], errors='coerce').fillna(0).astype(float)

    # Convertir 'Date' a formato de fecha para poder ordenarlo bien
    df_unido['Date'] = pd.to_datetime(df_unido['Date'])

    # Ordenar por fecha (de más nueva a vieja) y por Periodo (de temprano a tarde)
    df_unido = df_unido.sort_values(by=['Date', 'Period'], ascending=[False, True])

    # Convertir la fecha de vuelta a texto limpio (YYYY-MM-DD)
    df_unido['Date'] = df_unido['Date'].dt.strftime('%Y-%m-%d')

    # Guardar el archivo maestro
    df_unido.to_csv(archivo_salida, index=False)
    print(f"¡Listo! Tu tabla maestra se guardó como 'data_unificada_final.csv' en tu carpeta 'data limpia'.")

except FileNotFoundError as e:
    print(f"Error: No se encontró uno de los archivos. Asegúrate de que los nombres sean correctos.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")