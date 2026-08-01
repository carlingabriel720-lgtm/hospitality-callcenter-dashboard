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

archivo_html = os.path.join(os.path.dirname(archivo_csv), 'Executive_Operations_Dashboard.html')

try:
    print(f"¡Encontrado! Leyendo datos desde: {archivo_csv}")
    df = pd.read_csv(archivo_csv)
    
    # 1. DATA CLEANING & PREPARATION
    df['Period'] = df['Period'].astype(str).str.strip()
    df = df[df['Period'].str.contains(':', na=False)] 
    
    df['Day'] = df['Day'].astype(str).str.strip()
    df['Taken'] = pd.to_numeric(df['Taken'], errors='coerce').fillna(0)
    
    # Parse dates safely
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Year'] = df['Date'].dt.year.astype(int).astype(str)
    df['Month_Num'] = df['Date'].dt.month
    df['Month'] = df['Date'].dt.month_name()
    
    # Strict chronological orders
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meses_orden = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    periodos_ordenados = sorted(df['Period'].unique()) 
    
    # HIGH-CONTRAST LUXURY PALETTE
    luxury_color_map = {
        '2023': '#1A2530', 
        '2024': '#C5A059', 
        '2025': '#456990', 
        '2026': '#722F37'  
    }
    
    print("Generating elegant interactive charts...")

    # CONFIGURACIÓN DE LIMPIEZA DE METADATA
    config_clean = {
        'displaylogo': False, 
        'modeBarButtonsToRemove': ['sendDataToCloud', 'lasso2d', 'select2d'],
        'displayModeBar': 'hover'
    }

    # --- CHART 1: HEATMAP ---
    heatmap_data = df.groupby(['Day', 'Period'])['Taken'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Day', columns='Period', values='Taken').reindex(index=dias_orden, columns=periodos_ordenados)
    
    fig1 = px.imshow(heatmap_pivot, 
                     labels=dict(x="Time Period", y="Day of the Week", color="Avg. Calls"),
                     color_continuous_scale=['#F9F9F8', '#C5A059', '#1A2530'],
                     aspect="auto")
    
    fig1.update_xaxes(type='category')
    fig1.update_yaxes(type='category')
    fig1.update_layout(template='plotly_white', font=dict(family="Montserrat", size=12), 
                       margin=dict(l=20, r=20, t=20, b=20))

    # --- CHART 2: MONTHLY TREND ---
    monthly_data = df.groupby(['Year', 'Month_Num', 'Month'])['Taken'].sum().reset_index()
    monthly_data = monthly_data.sort_values(['Year', 'Month_Num'])
    
    fig2 = px.bar(monthly_data, x='Month', y='Taken', color='Year', barmode='group',
                  color_discrete_map=luxury_color_map, category_orders={"Year": ["2023", "2024", "2025", "2026"]})
    
    fig2.update_xaxes(categoryorder='array', categoryarray=meses_orden)
    fig2.update_layout(template='plotly_white', font=dict(family="Montserrat"),
                       legend_title="Click to Filter Year",
                       xaxis_title="", yaxis_title="Total Call Volume")

    # --- CHART 3: DAILY PATTERN ---
    daily_data = df.groupby(['Year', 'Day'])['Taken'].sum().reset_index()
    daily_data['Day'] = pd.Categorical(daily_data['Day'], categories=dias_orden, ordered=True)
    daily_data = daily_data.sort_values(['Year', 'Day'])
    
    fig3 = px.bar(daily_data, x='Day', y='Taken', color='Year', barmode='group',
                  color_discrete_map=luxury_color_map, category_orders={"Year": ["2023", "2024", "2025", "2026"]})
    fig3.update_layout(template='plotly_white', font=dict(family="Montserrat"),
                       legend_title="Click to Filter Year",
                       xaxis_title="", yaxis_title="Total Call Volume")

    # --- CHART 4: HOURLY DISTRIBUTION ---
    hourly_data = df.groupby(['Year', 'Period'])['Taken'].sum().reset_index()
    hourly_data['Period'] = pd.Categorical(hourly_data['Period'], categories=periodos_ordenados, ordered=True)
    hourly_data = hourly_data.sort_values(['Year', 'Period'])
    
    fig4 = px.line(hourly_data, x='Period', y='Taken', color='Year',
                   color_discrete_map=luxury_color_map, category_orders={"Year": ["2023", "2024", "2025", "2026"]}, line_shape='spline')
    
    fig4.update_layout(
        template='plotly_white', font=dict(family="Montserrat"),
        xaxis=dict(rangeslider=dict(visible=True), type="category", categoryarray=periodos_ordenados),
        legend_title="Click to Filter Year",
        xaxis_title="Time of Day", yaxis_title="Total Call Volume"
    )

    print("Assembling the Executive HTML Dashboard...")
    
    # 2. Assemble HTML with luxury CSS
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Executive Operations Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Montserrat:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Montserrat', sans-serif;
                background-color: #F4F4F6;
                color: #1A2530;
                margin: 0;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 60px;
                padding-bottom: 20px;
                border-bottom: 2px solid #C5A059;
            }}
            .header h1 {{
                font-family: 'Cinzel', serif;
                font-size: 2.8em;
                color: #1A2530;
                margin: 0;
                letter-spacing: 1px;
            }}
            .card {{
                background: white;
                padding: 40px;
                border-radius: 4px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.05);
                margin-bottom: 50px;
                border-top: 3px solid #C5A059;
            }}
            .card h2 {{
                font-family: 'Cinzel', serif;
                color: #1A2530;
                font-size: 1.8em;
                margin-top: 0;
                margin-bottom: 10px;
                border-bottom: 1px solid #EAEAEA;
                padding-bottom: 15px;
            }}
            .description {{
                font-size: 0.95em;
                color: #7F8C8D;
                line-height: 1.8;
                margin-bottom: 30px;
            }}
            .note {{
                font-weight: 600;
                color: #1A2530;
            }}
            .footer {{
                text-align: center;
                font-size: 0.85em;
                color: #7F8C8D;
                margin-top: 50px;
                font-family: 'Cinzel', serif;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Multi-Year Call Volume & Demand Analysis (2023-2026)</h1>
            </div>

            <div class="card">
                <h2>1. Shift Scheduling Heatmap</h2>
                <div class="description">
                    <span class="note">Operational Insight:</span> This matrix displays the average call volume per hour across different days of the week. Darker navy shades indicate peak saturation periods. Use this visual to justify staff allocation, structure team shifts, and optimize resource distribution during high-demand windows.
                </div>
                {fig1.to_html(full_html=False, include_plotlyjs='cdn', config=config_clean)}
            </div>

            <div class="card">
                <h2>2. Macro Seasonality & Monthly Trend</h2>
                <div class="description">
                    <span class="note">Operational Insight:</span> A year-over-year comparative analysis of total call volumes. This macroeconomic view assists executive planning by identifying seasonal peaks and low-traffic months, providing a data-driven foundation for annual budgeting and temporary hiring strategies.<br>
                    <i>* Interactive Filter: Click on the years in the legend to isolate specific timelines.</i>
                </div>
                {fig2.to_html(full_html=False, include_plotlyjs='cdn', config=config_clean)}
            </div>

            <div class="card">
                <h2>3. Weekly Effort Distribution</h2>
                <div class="description">
                    <span class="note">Operational Insight:</span> Illustrates the total operational load handled on each day of the week. Identifying which days bear the heaviest volume allows management to align IT infrastructure support, schedule maintenance during off-peak days, and balance workforce fatigue.<br>
                    <i>* Interactive Filter: Click on the years in the legend to toggle data visibility.</i>
                </div>
                {fig3.to_html(full_html=False, include_plotlyjs='cdn', config=config_clean)}
            </div>

            <div class="card">
                <h2>4. Hourly Demand Curve & Capacity</h2>
                <div class="description">
                    <span class="note">Operational Insight:</span> Tracks the exact trajectory of incoming demand throughout the day. By pinpointing the exact moments of demand drop-off (e.g., late evening), this model mathematically justifies the venue's opening and closing hours to maximize cost-efficiency.<br>
                    <i>* Interactive Filter: Use the slider directly below the chart to zoom into specific timeframes.</i>
                </div>
                {fig4.to_html(full_html=False, include_plotlyjs='cdn', config=config_clean)}
            </div>
            
            <div class="footer">
                Generated securely via Automated Python Architecture.
            </div>
        </div>
    </body>
    </html>
    """

    # Guardar el archivo HTML en la misma carpeta donde encontró el CSV
    with open(archivo_html, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"Success! The Executive Dashboard has been generated at:\n{archivo_html}")

except Exception as e:
    print(f"An error occurred: {e}")