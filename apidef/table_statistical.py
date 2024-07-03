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
            cell.set(facecolor='grey')

        # Second column
        elif col == 2:
            val = float(cell.get_text().get_text())
            left_val = float(table[row, col - 1].get_text().get_text())
            if val <= left_val:
                cell.set_text_props(color='green')
            else:
                cell.set_text_props(color='red')

def build_statistical_table(con):
    time_type, time, loc = extract_request_statistical_params()

    pop_RS = 11300000
    pop_Ijui = 83000
    parcela_pop = 100000

    # Cálculo das métricas para o estado
    acidentes_RS = population_df(con, time_type, time)
    acidentes_RS['Quantidade_Acidentes'] = (acidentes_RS['Quantidade_Acidentes'] / pop_RS) * parcela_pop
    metricas_RS = acidentes_RS['Quantidade_Acidentes'].describe()
    variancia_RS = acidentes_RS['Quantidade_Acidentes'].var()

    # Cálculo das métricas para a microrregião de Ijuí
    acidentes_Ijui = sample_df(con, time_type, time, loc)
    acidentes_Ijui['Quantidade_Acidentes'] = (acidentes_Ijui['Quantidade_Acidentes'] / pop_Ijui) * parcela_pop
    metricas_Ijui = acidentes_Ijui['Quantidade_Acidentes'].describe()
    variancia_Ijui = acidentes_Ijui['Quantidade_Acidentes'].var()

    # Exibição das métricas
    metricas_estatisticas = pd.DataFrame({
        'Métrica': ['Média', 'Mediana', 'Desvio Padrão', 'Variância', 'Máximo', 'Mínimo'],
        'RS': [
            metricas_RS['mean'], metricas_RS['50%'], metricas_RS['std'], 
            variancia_RS, metricas_RS['max'], metricas_RS['min']
        ],
        'Ijuí': [
            metricas_Ijui['mean'], metricas_Ijui['50%'], metricas_Ijui['std'], 
            variancia_Ijui, metricas_Ijui['max'], metricas_Ijui['min']
        ]
    })

    # Formatar os valores para 2 casas decimais
    metricas_estatisticas['RS'] = metricas_estatisticas['RS'].round(2)
    metricas_estatisticas['Ijuí'] = metricas_estatisticas['Ijuí'].round(2)

    # print(metricas_estatisticas)
    fig, ax = plt.subplots() # figsize=(10, 4))

    table = ax.table(cellText=metricas_estatisticas.values,
        # rowLabels=metricas_estatisticas['Métrica'], 
        # colLabels=metricas_estatisticas[['RS', 'Ijui']].columns,
        colLabels=metricas_estatisticas.columns,
        cellLoc='center', colLoc='center', rowLoc='center', loc='center')

    style_table(table)

    ax.axis('tight')
    ax.axis('off')
    ax.set_title(f'''Análise de Variância Proporcional da Quantidade Mensal de
Acidentes por 100.000 Habitantes no Ano de {time}:
Comparação entre o Rio Grande do Sul e a Cidade de Ijuí''', y = 0.675)

    return fig

def build_statistical_table_other(con):
    time_type, time, loc = extract_request_statistical_params()

    # pop_Sant = 83000
    # pop_Ijui = 83000
    # parcela_pop = 100000

    nome_outro = get_city_name(con, loc) # 'Cachoeira do Sul'
    cod_outro = loc # '430300'

    # Cálculo das métricas para o estado
    acidentes_Outro = sample_df(con, time_type, time, cod_outro)
    # acidentes_Outro['Quantidade_Acidentes'] = (acidentes_Outro['Quantidade_Acidentes'] / pop_RS) * parcela_pop
    metricas_Outro = acidentes_Outro['Quantidade_Acidentes'].describe()
    variancia_Outro = acidentes_Outro['Quantidade_Acidentes'].var()

    # Cálculo das métricas para a microrregião de Ijuí
    acidentes_Ijui = sample_df(con, time_type, time, '431020')
    # acidentes_Ijui['Quantidade_Acidentes'] = (acidentes_Ijui['Quantidade_Acidentes'] / pop_Ijui) * parcela_pop
    metricas_Ijui = acidentes_Ijui['Quantidade_Acidentes'].describe()
    variancia_Ijui = acidentes_Ijui['Quantidade_Acidentes'].var()

    # Exibição das métricas
    metricas_estatisticas = pd.DataFrame({
        'Métrica': ['Média', 'Mediana', 'Desvio Padrão', 'Variância', 'Máximo', 'Mínimo'],
        nome_outro: [
            metricas_Outro['mean'], metricas_Outro['50%'], metricas_Outro['std'], 
            variancia_Outro, metricas_Outro['max'], metricas_Outro['min']
        ],
        'Ijuí': [
            metricas_Ijui['mean'], metricas_Ijui['50%'], metricas_Ijui['std'], 
            variancia_Ijui, metricas_Ijui['max'], metricas_Ijui['min']
        ]
    })

    # Formatar os valores para 2 casas decimais
    metricas_estatisticas[nome_outro] = metricas_estatisticas[nome_outro].round(2)
    metricas_estatisticas['Ijuí'] = metricas_estatisticas['Ijuí'].round(2)

    # print(metricas_estatisticas)
    fig, ax = plt.subplots() # figsize=(10, 4))

    table = ax.table(cellText=metricas_estatisticas.values,
        # rowLabels=metricas_estatisticas['Métrica'], 
        # colLabels=metricas_estatisticas[['RS', 'Ijui']].columns,
        colLabels=metricas_estatisticas.columns,
        cellLoc='center', colLoc='center', rowLoc='center', loc='center')

    style_table(table)

    ax.axis('tight')
    ax.axis('off')
    ax.set_title(f'''Análise de Variância da Quantidade Mensal de Acidentes no Ano
de {time}: Comparação entre as Cidades de {nome_outro} e Ijuí''', y = 0.675)

    return fig

