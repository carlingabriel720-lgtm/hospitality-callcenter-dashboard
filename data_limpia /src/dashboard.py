import pandas as pd
import plotly.express as px
import os

# Buscar automáticamente 'data_unificada_final.csv' en todo el Escritorio y subcarpetas
desktop = os.path.expanduser('~/Desktop')
archivo_csv = None

print("Buscando 'data_unificada_final.csv' en el Escritorio...")
for root, dirs, files in os.walk(desktop):
    if 'data_unificada_final.csv' in files:
        archivo_csv = os.path.join(root, 'data_unificada_final.csv')
        break

if not archivo_csv:
    raise FileNotFoundError("No se encontró el archivo 'data_unificada_final.csv' en tu Escritorio o subcarpetas.")

archivo_html = os.path.join(os.path.dirname(archivo_csv), 'index.html')

try:
    print(f"¡Encontrado! Leyendo datos desde: {archivo_csv}")
    df = pd.read_csv(archivo_csv)
    
    # 1. LIMPIEZA Y PREPARACIÓN DE DATOS
    df['Period'] = df['Period'].astype(str).str.strip()
    df = df[df['Period'].str.contains(':', na=False)] 
    
    df['Day'] = df['Day'].astype(str).str.strip()
    df['Taken'] = pd.to_numeric(df['Taken'], errors='coerce').fillna(0)
    
    # Parseo seguro de fechas
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Year'] = df['Date'].dt.year.astype(int).astype(str)
    df['Month_Num'] = df['Date'].dt.month
    df['Month'] = df['Date'].dt.month_name()
    
    # Órdenes cronológicos estrictos (los datos originales están en inglés)
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meses_orden = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    periodos_ordenados = sorted(df['Period'].unique()) 
    
    # PALETA DE COLORES GOOGLE (Material Design)
    google_color_map = {
        '2023': '#4285F4', # Azul Google
        '2024': '#EA4335', # Rojo Google
        '2025': '#FBBC05', # Amarillo Google
        '2026': '#34A853'  # Verde Google
    }
    
    print("Generando gráficos interactivos con estilo Google...")

    # CONFIGURACIÓN DE LIMPIEZA DE METADATA (Plotly)
    config_clean = {
        'displaylogo': False, 
        'modeBarButtonsToRemove': ['sendDataToCloud', 'lasso2d', 'select2d'],
        'displayModeBar': 'hover'
    }

    # --- GRÁFICO 1: MAPA DE CALOR ---
    heatmap_data = df.groupby(['Day', 'Period'])['Taken'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Day', columns='Period', values='Taken').reindex(index=dias_orden, columns=periodos_ordenados)
    
    fig1 = px.imshow(heatmap_pivot, 
                     labels=dict(x="Franja Horaria", y="Día de la Semana", color="Promedio"),
                     color_continuous_scale=['#F8F9FA', '#8AB4F8', '#174EA6'], # De blanco/gris a azul oscuro
                     aspect="auto")
    
    fig1.update_xaxes(type='category')
    fig1.update_yaxes(type='category')
    fig1.update_layout(template='plotly_white', font=dict(family="Roboto", size=12, color="#202124"), 
                       margin=dict(l=20, r=20, t=20, b=20))

    # --- GRÁFICO 2: TENDENCIA MENSUAL ---
    monthly_data = df.groupby(['Year', 'Month_Num', 'Month'])['Taken'].sum().reset_index()
    monthly_data = monthly_data.sort_values(['Year', 'Month_Num'])
    
    fig2 = px.bar(monthly_data, x='Month', y='Taken', color='Year', barmode='group',
                  color_discrete_map=google_color_map, category_orders={"Year": ["2023", "2024", "2025", "2026"]})
    
    fig2.update_xaxes(categoryorder='array', categoryarray=meses_orden, title="")
    fig2.update_layout(template='plotly_white', font=dict(family="Roboto", color="#202124"),
                       legend_title="Filtrar por Año", yaxis_title="Volumen Total de Llamadas")

    # --- GRÁFICO 3: PATRÓN DIARIO ---
    daily_data = df.groupby(['Year', 'Day'])['Taken'].sum().reset_index()
    daily_data['Day'] = pd.Categorical(daily_data['Day'], categories=dias_orden, ordered=True)
    daily_data = daily_data.sort_values(['Year', 'Day'])
    
    fig3 = px.bar(daily_data, x='Day', y='Taken', color='Year', barmode='group',
                  color_discrete_map=google_color_map, category_orders={"Year": ["2023", "2024", "2025", "2026"]})
    fig3.update_layout(template='plotly_white', font=dict(family="Roboto", color="#202124"),
                       legend_title="Filtrar por Año",
                       xaxis_title="", yaxis_title="Volumen Total de Llamadas")

    # --- GRÁFICO 4: DISTRIBUCIÓN POR HORA ---
    hourly_data = df.groupby(['Year', 'Period'])['Taken'].sum().reset_index()
    hourly_data['Period'] = pd.Categorical(hourly_data['Period'], categories=periodos_ordenados, ordered=True)
    hourly_data = hourly_data.sort_values(['Year', 'Period'])
    
    fig4 = px.line(hourly_data, x='Period', y='Taken', color='Year',
                   color_discrete_map=google_color_map, category_orders={"Year": ["2023", "2024", "2025", "2026"]}, line_shape='spline')
    
    fig4.update_layout(
        template='plotly_white', font=dict(family="Roboto", color="#202124"),
        xaxis=dict(rangeslider=dict(visible=True), type="category", categoryarray=periodos_ordenados),
        legend_title="Filtrar por Año",
        xaxis_title="Franja Horaria", yaxis_title="Volumen Total de Llamadas"
    )

    print("Ensamblando el Dashboard en HTML...")
    
    # 2. ENSAMBLAJE DEL HTML CON CSS ESTILO MATERIAL DESIGN (GOOGLE)
    html_template = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard Analítico de Operaciones</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Roboto', sans-serif;
                background-color: #F8F9FA; /* Gris ultra claro estilo Google */
                color: #202124; /* Gris oscuro texto Google */
                margin: 0;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: auto;
            }}
            .header {{
                margin-bottom: 40px;
                padding-bottom: 20px;
            }}
            .header h1 {{
                font-size: 2.5em;
                font-weight: 400;
                color: #202124;
                margin: 0;
            }}
            .header p {{
                color: #5F6368;
                font-size: 1.1em;
                margin-top: 8px;
            }}
            .card {{
                background: #FFFFFF;
                padding: 35px;
                border-radius: 8px;
                border: 1px solid #DADCE0; /* Borde sutil Material Design */
                margin-bottom: 40px;
            }}
            .card h2 {{
                color: #202124;
                font-size: 1.5em;
                font-weight: 500;
                margin-top: 0;
                margin-bottom: 12px;
            }}
            .description {{
                font-size: 0.95em;
                color: #5F6368;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .note {{
                font-weight: 500;
                color: #1A73E8; /* Azul primario de enlaces Google */
            }}
            .footer {{
                text-align: center;
                font-size: 0.85em;
                color: #9AA0A6;
                margin-top: 50px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Análisis de Demanda y Volumen de Operaciones</h1>
                <p>Reporte consolidado multi-anual (2023 - 2026)</p>
            </div>

            <div class="card">
                <h2>1. Mapa de Calor (Distribución de Turnos)</h2>
                <div class="description">
                    <span class="note">Insight Operativo:</span> Esta matriz muestra el volumen promedio de llamadas por hora según el día de la semana. Los tonos azules más intensos indican periodos de máxima saturación. Utilice este panel para estructurar los turnos del equipo y optimizar la asignación de recursos.
                </div>
                {fig1.to_html(full_html=False, include_plotlyjs='cdn', config=config_clean)}
            </div>

            <div class="card">
                <h2>2. Estacionalidad Macro y Tendencia Mensual</h2>
                <div class="description">
                    <span class="note">Insight Operativo:</span> Análisis comparativo interanual de la carga operativa. Esta vista macroeconómica permite identificar picos estacionales y meses de bajo tráfico, brindando una base para la planificación de presupuestos y contrataciones temporales.<br>
                    <i>* Interactividad: Haz clic en los años de la leyenda para aislar métricas específicas.</i>
                </div>
                {fig2.to_html(full_html=False, include_plotlyjs='cdn', config=config_clean)}
            </div>

            <div class="card">
                <h2>3. Distribución Semanal de Esfuerzo</h2>
                <div class="description">
                    <span class="note">Insight Operativo:</span> Ilustra la carga operativa total manejada cada día de la semana. Identificar los días de mayor tráfico permite alinear el soporte de infraestructura técnica y prevenir la fatiga de la fuerza laboral.<br>
                    <i>* Interactividad: Haz clic en la leyenda para ocultar o mostrar años.</i>
                </div>
                {fig3.to_html(full_html=False, include_plotlyjs='cdn', config=config_clean)}
            </div>

            <div class="card">
                <h2>4. Curva de Demanda y Capacidad por Hora</h2>
                <div class="description">
                    <span class="note">Insight Operativo:</span> Rastrea la trayectoria exacta de la demanda entrante durante el día. Al identificar los momentos exactos en que la demanda disminuye, este modelo justifica matemáticamente los horarios de apertura y cierre para maximizar la eficiencia de costos.<br>
                    <i>* Interactividad: Utiliza la barra deslizable debajo de la gráfica para hacer zoom en franjas específicas.</i>
                </div>
                {fig4.to_html(full_html=False, include_plotlyjs='cdn', config=config_clean)}
            </div>
            
            <div class="footer">
                Generado automáticamente mediante arquitectura de datos en Python.
            </div>
        </div>
    </body>
    </html>
    """

    # Guardar el archivo HTML
    with open(archivo_html, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"¡Éxito! El Dashboard HTML ha sido generado en:\n{archivo_html}")

except Exception as e:
    print(f"Ocurrió un error: {e}")