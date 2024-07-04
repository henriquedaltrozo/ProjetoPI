from apidef.util.custom_plots import get_city_name
import matplotlib.pyplot as plt
from flask import request
import pandas as pd

# ?localizacao=200300&tipo-tempo=mensal&tempo=201911
# ?localizacao=200300&tipo-tempo=anual&tempo=2019
def extract_request_statistical_params():
    time_type = request.args.get('tipo-tempo')
    time_type = time_type if time_type != None else 'anual'

    time = request.args.get('tempo')
    time = time if time != None else '2016-2024'

    loc = request.args.get('localizacao')
    loc = loc if loc != None else '431020' # Default to Ijui

    return time_type, time, loc

def population_df(con, time_type, time):
    # select, where = 'mes', 'pa_cmp' if time_type == 'mensal' else 'ano', 'ano';

    # statement = f'''
    # SELECT {select}, {qtd_val_sql}
    # FROM fato_pars 
    # JOIN dim_tempo ON pa_cmp = id
    # JOIN dim_localizacao ON mun_id = pa_munpcn 
    # JOIN ANOMESC ON pa_cmp = codigo
    # WHERE {where} = {time}
    # GROUP BY {select}
    # ORDER BY {select}
    # '''

    statement = f'''
    SELECT ano, mes, c as Quantidade_Acidentes 
    FROM (
        SELECT pa_cmp, COUNT(*) as c
        FROM fato_pars 
        GROUP BY pa_cmp
    ) 
    JOIN dim_tempo ON pa_cmp = id 
    WHERE ano = {time} 
    ORDER BY mes
    '''

    return con.execute(statement).df()

def sample_df(con, time_type, time, loc):
    # select, where = 'mes', 'pa_cmp' if time_type == 'mensal' else 'ano', 'ano';

    statement = f'''
    SELECT ano, mes, c as Quantidade_Acidentes 
    FROM (
        SELECT pa_cmp, COUNT(*) as c
        FROM fato_pars 
        WHERE pa_munpcn = {loc}
        GROUP BY pa_cmp
    ) 
    JOIN dim_tempo ON pa_cmp = id 
    WHERE ano = {time}
    ORDER BY mes
    '''

    return con.execute(statement).df()

def style_table(table):
    for (row, col), cell in table.get_celld().items():
        # print(row, col, cell.get_text())

        # First row
        if row == 0:
            cell.set_text_props(fontweight='bold')
            cell.set(facecolor='cornflowerblue')

        # First column
        elif col == 0:
            cell.set_text_props(fontweight='bold')
            if row > 0 and row <= 2:
                cell.set(facecolor='powderblue')
            elif row > 2 and row <= 5:
                cell.set(facecolor='thistle')
            else:
                cell.set(facecolor='palegoldenrod')

        # Second column, color metrics as good or bad
        elif col == 2 and row <= 5:
            val = float(cell.get_text().get_text())
            left_val = float(table[row, col - 1].get_text().get_text())
            if val <= left_val:
                cell.set_text_props(color='green')
            else:
                cell.set_text_props(color='red')

        # Put % in CV
        if col > 0 and row == 8:
            val = float(cell.get_text().get_text())
            cell.set_text_props(text=f'{val:.2f}%')

def gen_metrics(df, col):
    metrics = df[col].describe()

    mn = metrics['min']
    mx = metrics['max']

    mean   = metrics['mean']
    median = metrics['50%']
    mode   = df[col].mode().iloc[0]

    var = df[col].var()
    std = metrics['std']
    cv  = (std / mean) * 100

    return [mn, mx, mean, median, mode, var, std, cv]

def build_comparative_df(df_a, name_a, df_b, name_b, col):
    metrics_a = gen_metrics(df_a, col)
    metrics_b = gen_metrics(df_b, col)

    # Exibição das métricas
    comparative_df = pd.DataFrame({
        'Métricas': ['Mínimo', 'Máximo', 'Média', 'Mediana', 'Moda', 'Variância', 'Desvio Padrão', 'CV'],
        name_a: metrics_a,
        name_b: metrics_b
    })

    # Formatar os valores para 2 casas decimais
    comparative_df[name_a] = comparative_df[name_a].round(2)
    comparative_df[name_b] = comparative_df[name_b].round(2)

    return comparative_df

import duckdb
def build_statistical_table(con):
    time_type, time, loc = extract_request_statistical_params()

    pop_RS = 11300000
    pop_Ijui = 83000
    parcela_pop = 100000

    # con_1 = duckdb.connect('database.db')
    acidentes_RS = population_df(con, time_type, time)
    acidentes_RS['Quantidade_Acidentes'] = (acidentes_RS['Quantidade_Acidentes'] / pop_RS) * parcela_pop

    # con_1 = duckdb.connect('database.db')
    acidentes_Ijui = sample_df(con, time_type, time, loc)
    acidentes_Ijui['Quantidade_Acidentes'] = (acidentes_Ijui['Quantidade_Acidentes'] / pop_Ijui) * parcela_pop

    df = build_comparative_df(acidentes_RS, 'RS', acidentes_Ijui, 'Ijuí', 'Quantidade_Acidentes')

    # print(metricas_estatisticas)
    fig, ax = plt.subplots() # figsize=(10, 4))

    table = ax.table(cellText=df.values,
        # rowLabels=metricas_estatisticas['Métrica'], 
        # colLabels=metricas_estatisticas[['RS', 'Ijui']].columns,
        colLabels=df.columns,
        cellLoc='center', colLoc='center', rowLoc='center', loc='center')

    style_table(table)

    ax.axis('tight')
    ax.axis('off')
    ax.set_title(f'''Análise de Variância Proporcional da Quantidade Mensal de
Acidentes por 100.000 Habitantes no Ano de {time}:
Comparação entre o Rio Grande do Sul e a Cidade de Ijuí''', y = 0.7)

    return fig

def build_statistical_table_other(con):
    time_type, time, loc = extract_request_statistical_params()

    # pop_Sant = 83000
    # pop_Ijui = 83000
    # parcela_pop = 100000

    nome_outro = get_city_name(con, loc) # 'Cachoeira do Sul'
    cod_outro = loc # '430300'
    acidentes_outro = sample_df(con, time_type, time, cod_outro)
    # acidentes_Outro['Quantidade_Acidentes'] = (acidentes_Outro['Quantidade_Acidentes'] / pop_RS) * parcela_pop

    acidentes_ijui = sample_df(con, time_type, time, '431020')
    # acidentes_Ijui['Quantidade_Acidentes'] = (acidentes_Ijui['Quantidade_Acidentes'] / pop_Ijui) * parcela_pop

    df = build_comparative_df(acidentes_outro, nome_outro, acidentes_ijui, 'Ijuí', 'Quantidade_Acidentes')

    # print(metricas_estatisticas)
    fig, ax = plt.subplots() # figsize=(10, 4))

    table = ax.table(cellText=df.values,
        # rowLabels=metricas_estatisticas['Métrica'], 
        # colLabels=metricas_estatisticas[['RS', 'Ijui']].columns,
        colLabels=df.columns,
        cellLoc='center', colLoc='center', rowLoc='center', loc='center')

    style_table(table)

    ax.axis('tight')
    ax.axis('off')
    ax.set_title(f'''Análise Estatística da Quantidade Mensal de Acidentes no Ano
de {time}: Comparação entre as Cidades de {nome_outro} e Ijuí''', y = 0.7)

    return fig

