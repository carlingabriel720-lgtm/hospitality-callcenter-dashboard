import pandas as pd

# Archivos de entrada y salida apuntando directo a tu escritorio
archivo_entrada = '/Users/*****/Desktop/Calls report.csv'
archivo_salida = '/Users/*****/Desktop/data_limpia_y_ordenada.csv'

try:
    print("Cargando los datos...")
    df = pd.read_csv(archivo_entrada)

    # Limpiar espacios en los nombres de las columnas
    df.columns = df.columns.str.strip()

    # Convertir la columna 'Date' a formato de fecha
    df['Date'] = pd.to_datetime(df['Date'])

    # Ordenar
    df_ordenado = df.sort_values(by='Date', ascending=False)

    # Guardar
    df_ordenado.to_csv(archivo_salida, index=False)
    print(f"¡Listo! La data se ha guardado en tu escritorio como '{archivo_salida}'.")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{archivo_entrada}'.")
except KeyError as e:
    print(f"Error: No se encontró la columna {e}.")