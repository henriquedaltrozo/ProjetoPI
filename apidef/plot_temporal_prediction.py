from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from apidef.util.custom_plots import get_city_name
from pmdarima import auto_arima
import matplotlib.pyplot as plt
from flask import request
import pandas as pd
import numpy as np
import duckdb

# ?tipo-tempo=mensal/anual
# ?tempo=2019-2023
def extract_request_loc_params():
    # time_type = request.args.get('tipo-tempo')
    # time_type = time_type if time_type != None else 'anual'

    # time = request.args.get('tempo')
    # time = time if time != None else '2016-2024'

    loc_type = request.args.get('tipo-localizacao')
    loc_type = loc_type if loc_type != None else 'estado'

    loc = request.args.get('localizacao')
    loc = loc if loc != None else '431020'

    return loc_type, loc

def total_monthly_df(con):
    statement = f'''
    SELECT ano, mes, c as Quantidade_Acidentes 
    FROM (
        SELECT pa_cmp, COUNT(*) as c
        FROM fato_pars 
        GROUP BY pa_cmp
    ) 
    JOIN dim_tempo ON pa_cmp = id 
    ORDER BY mes
    '''

    return con.execute(statement).df()

def build_pdt_test_plot(con, params):
    df = total_monthly_df(con)
    df = df[df['ano'] >= 2020]

    # Criação da coluna de período
    df['Periodo'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)
    df['Periodo'] = pd.to_datetime(df['Periodo'], format='%Y-%m')
    df.set_index('Periodo', inplace=True)

    # Ordenar os dados por período
    df = df.sort_index()

    # Aplicar o modelo de média móvel com uma janela de 3 meses
    df['MA_3'] = df['Quantidade_Acidentes'].rolling(window=3).mean()

    # Melhores: (3, 2, 5), (4, 2, 5), (4, 3, 4)
    pr = range(1, 6)
    dr = range(1, 6)
    qr = range(6, 8)

    fig, ax = plt.subplots(
        figsize=(10, 30), 
        nrows=(pr[-1] - pr[0]) * (dr[-1] - dr[0]) * (qr[-1] - qr[0])
    )

    # Aplicar o modelo ARIMA para fazer previsões
    # Ajustar o modelo ARIMA (Ajuste de parâmetros p, d, q conforme necessário)
    i = 0
    for p in pr:
        for d in dr:
            for q in qr:
                model = ARIMA(df['Quantidade_Acidentes'], order=(p, d, q)) # order=(0, 0, 1))
                fit = model.fit(method_kwargs={'maxiter':300})

                # Fazer previsões para os próximos 10 meses
                forecast = fit.forecast(steps=10)
                # print(forecast)

                # Plotar os dados históricos e a média móvel
                ax[i].plot(df.index, df['Quantidade_Acidentes'], label='Dados Históricos')
                ax[i].plot(df.index, df['MA_3'], label='Média Móvel (3 meses)', linestyle='--')
                ax[i].plot(forecast.index, forecast, label='Previsões ARIMA', linestyle='--', marker='o')
                # ax[i].set_xlabel('Período')
                ax[i].set_ylabel('Quantidade de Acidentes')
                ax[i].set_title(f'({p} {d} {q}) Análise de Acidentes de Trânsito com Média Móvel')
                ax[i].legend()

                i+=1

    return fig

def build_my_little_title(con, loc_type, loc):
    city_name = get_city_name(con, loc)

    loc_str = ''
    if loc_type == 'cidade':
        loc_str = f'na Cidade de {city_name} - RS'
    elif loc_type == 'microrregiao':
        loc_str = f'na Microrregião de {city_name} - RS'
    elif loc_type == 'estado':
        loc_str = f'no Estado do Rio Grande do Sul'

    title =   'Modelo Preditivo e Média Móvel da Quantidade de Atendimentos\n'
    title += f'Relacionados a Acidentes de Trânsito {loc_str}'

    return title

def build_temporal_prediction_plot(con):
    loc_type, loc = extract_request_loc_params()

    df = total_monthly_df(con)
    df = df[df['ano'] >= 2020]

    # Criação da coluna de período
    df['Periodo'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)
    df['Periodo'] = pd.to_datetime(df['Periodo'], format='%Y-%m')
    df.set_index('Periodo', inplace=True)

    # Ordenar os dados por período
    df = df.sort_index()

    # Aplicar o modelo de média móvel com uma janela de 3 meses
    df['MA_3'] = df['Quantidade_Acidentes'].rolling(window=3).mean()

    # Aplicar o modelo ARIMA para fazer previsões
    # model = ARIMA(df['Quantidade_Acidentes'], order=(p, d, q)) # order=(0, 0, 1))
    # fit = model.fit(method_kwargs={'maxiter':300})

    # Fazer previsões para os próximos 10 meses
    # forecast = fit.forecast(steps=10)
    # print(forecast)

    # Determinar a sazonalidade (anual - 12 meses)
    seasonal_period = 12
    
    # Seasonal Arima
    sarima_model = auto_arima(df['Quantidade_Acidentes'], 
        seasonal=True, m=seasonal_period,
        stepwise=True, trace=True
    )

    # Faz a predição dos próximos meses
    forecast = sarima_model.predict(n_periods=12)

    fig, ax = plt.subplots() # figsize=(15, 10))

    # Plotar os dados históricos, a média móvel e a predição
    ax.plot(df.index, df['Quantidade_Acidentes'], label='Dados Históricos')
    ax.plot(df.index, df['MA_3'], label='Média Móvel (3 meses)', linestyle='--')
    ax.plot(forecast.index, forecast, label='Previsões', linestyle='--', marker='.')

    ax.set_xlabel('Período')
    ax.set_ylabel('Quantidade de Acidentes')
    ax.set_title(build_my_little_title(con, loc_type, loc))
    ax.legend()

    return fig

