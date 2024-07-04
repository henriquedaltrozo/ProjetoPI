from apidef.util.custom_plots import *
import matplotlib.pyplot as plt
from flask import request
import numpy as np
import duckdb

# ?tipo-tempo=mensal/anual
# ?tempo=2019-2023
def extract_request_time_params():
    time_type = request.args.get('tipo-tempo')
    time_type = time_type if time_type != None else 'anual'

    time = request.args.get('tempo')
    time = time if time != None else '2016-2024'

    return time_type, time

def build_time_sql(time_type, time):
    first, last = tuple(time.split('-'))
    years = range(int(first), int(last) + 1)

    return 'WHERE' + 'OR'.join([f" ano = '{year}' " for year in years])

def build_temporal_plot(con, params):
    var_type, top, loc_type, loc = params
    time_type, time = extract_request_time_params()

    loc_sql = build_loc_sql(loc_type, loc)
    qtd_val_sql = build_qtd_val_sql(var_type)
    time_sql = build_time_sql(time_type, time)

    fig, ax = plt.subplots()

    if time_type == 'anual':
        statement = f'''
        SELECT * 
        FROM (
            SELECT ano, {qtd_val_sql}
            FROM fato_pars 
            JOIN dim_tempo ON pa_cmp = id
            JOIN dim_localizacao ON mun_id = pa_munpcn 
            JOIN ANOMESC ON pa_cmp = codigo
            {loc_sql}
            GROUP BY ano
            ORDER BY ano
        )
        {time_sql}
        '''

        con.execute(statement)

        result = con.fetchall()
        unzipped = list(zip(*result))
        x = list(unzipped[0])
        y = list(unzipped[1])

        plotted = ax.plot(x, y, label=f'{time}')

        # Linha de tendencia central
        X = np.arange(len(x))
        z = np.poly1d(np.polyfit(X, y, 1))
        ax.plot(x, z(X), '--', label=f'Tendência: {year}', 
            alpha=0.6, color=plotted[0].get_color())
    elif time_type == 'mensal':
        first, last = tuple(time.split('-'))
        for year in range(int(first), int(last) + 1):
            where_sql = f"WHERE ano = '{year}'"
            if loc_sql != '':
                where_sql += f' AND {loc_sql[6:]}'

            statement = f'''
            SELECT mes, {qtd_val_sql}
            FROM fato_pars 
            JOIN dim_tempo ON pa_cmp = id
            JOIN dim_localizacao ON mun_id = pa_munpcn 
            JOIN ANOMESC ON pa_cmp = codigo
            {where_sql}
            GROUP BY mes
            ORDER BY mes
            '''

            con.execute(statement)

            months = [
                "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", 
                "Jul", "Ago", "Set", "Out", "Nov", "Dez"
            ]

            result = con.fetchall()
            unzipped = list(zip(*result))
            x = list(unzipped[0])
            y = list(unzipped[1])

            for month in range(1, 13):
                if not month in x:
                    x.insert(month - 1, month)
                    y.insert(month - 1, 0)

            # x = list(map(lambda ym: ym[ym.find('/')+1:], list(unzipped[0])))
            x = list(map(lambda m: months[int(m) - 1], x))

            plotted = ax.plot(x, y, label=f'{year}')

            # Linha de tendencia central
            X = np.arange(len(x))
            z = np.poly1d(np.polyfit(X, y, 1))
            ax.plot(x, z(X), '--', label=f'Tendência: {year}', 
                alpha=0.6, color=plotted[0].get_color())

    ax.set_ylabel('Número de Atendimentos')
    ax.set_xlabel('Mês')
    ax.set_title(build_plot_title(con, params, 'Ano'))
    ax.legend()

    return fig
