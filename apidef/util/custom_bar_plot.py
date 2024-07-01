from apidef.util.custom_plots import *
import matplotlib.pyplot as plt
import duckdb

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
        JOIN dim_localizacao ON mun_id = pa_munpcn 
        {loc_sql}
        GROUP BY {group_by}
    ) 
    {join_outside_sql}
    ORDER BY apr DESC 
    LIMIT {top}
    '''
    
    custom_bar_plot_statement(con, ax, top, statement)

