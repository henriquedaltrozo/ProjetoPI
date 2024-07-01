import matplotlib.pyplot as plt
from random import randint
import numpy as np
import duckdb

def random_colors(n):
    r = np.random.rand(n)
    g = np.random.rand(n)
    b = np.random.rand(n)

    return list(zip(r, g, b))

city_names = {}
def get_city_name(con, loc):
    global city_names

    # If city_names is empty, populate it from the database
    if (not city_names):
        con.execute('SELECT mun_id, mun_nome FROM dim_localizacao')
        city_names = { str(id): name.title() for id, name in con.fetchall() }

    return city_names[loc]

def build_loc_sql(loc_type, loc):
    loc_sql = '' # Estado
    if loc_type == 'cidade':
        loc_sql = f'WHERE pa_munpcn = {loc}'
    elif loc_type == 'microrregiao':
        loc_sql = f'WHERE mic_id = {loc}'

    return loc_sql

def build_qtd_val_sql(var_type):
    return 'SUM(pa_valapr)' if var_type == 'valor' else 'COUNT(pa_qtdapr)'

def build_plot_title(con, params, topic):
    var_type, top, loc_type, loc = params

    city_name = get_city_name(con, loc)

    loc_str = ''
    if loc_type == 'cidade':
        loc_str = f'na Cidade de {city_name} - RS'
    elif loc_type == 'microrregiao':
        loc_str = f'na Microrregião de {city_name} - RS'
    elif loc_type == 'estado':
        loc_str = f'no Estado do Rio Grande do Sul'

    title = f'''
    Quantidade de Atendimentos Relacionados a Acidentes de Trânsito
    por {topic} {loc_str}'''

    return title

