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
        loc_sql = f'JOIN dim_localizacao ON mun_id = pa_munpcn WHERE mic_id = {loc}'

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

def custom_bar_plot_statement(con, ax, top, statement):
    # var_type, top, loc_type, loc = params

    # df = duckdb.sql(statement).df()
    con.execute(statement)

    result = con.fetchall()
    unzipped = list(zip(*result))
    x = [f'{str(i + 1)}°' for i in range(int(top))]
    y = list(unzipped[1])

    ax.bar(x, y, color=random_colors(int(top)), label=list(unzipped[0]))

def custom_bar_plot(con, ax, params, dim, x, group_by=None, join_inside=False):
    var_type, top, loc_type, loc = params

    loc_sql = build_loc_sql(loc_type, loc)
    qtd_val_sql = build_qtd_val_sql(var_type)

    if group_by == None:
        group_by = x

    join_outside_sql = f'JOIN {dim[0]} ON {dim[1]} = {x}'
    join_inside_sql = ''
    if join_inside:
        join_inside_sql = join_outside_sql
        join_outside_sql = ''

    statement = f'''
    SELECT {dim[2]} AS x, apr 
    FROM (
        SELECT {group_by}, {qtd_val_sql} AS apr 
        FROM fato_pars 
        {join_inside_sql}
        {loc_sql}
        GROUP BY {group_by}
    ) 
    {join_outside_sql}
    ORDER BY apr DESC 
    LIMIT {top}
    '''
    
    custom_bar_plot_statement(con, ax, top, statement)

