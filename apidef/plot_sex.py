from apidef.util.custom_plots import *
import matplotlib.pyplot as plt
import duckdb

def build_sex_plot(con, params):
    var_type, top, loc_type, loc = params

    loc_sql = build_loc_sql(loc_type, loc)
    qtd_val_sql = build_qtd_val_sql(var_type)

    statement = f'''
    SELECT pa_sexo, {qtd_val_sql} AS apr 
    FROM fato_pars 
    {loc_sql}
    GROUP BY pa_sexo
    ORDER BY apr DESC 
    LIMIT {top}
    '''
    
    con.execute(statement)

    result = con.fetchall()
    unzipped = list(zip(*result))
    x = ['Masculino', 'Feminino']
    y = list(unzipped[1])

    fig, ax = plt.subplots()

    wedges, texts, autotexts = ax.pie(y, 
        autopct=lambda val: f'{val:.1f}%', 
        colors=['cornflowerblue', 'hotpink'],
        textprops=dict(color="w"))

    ax.set_xlabel('Porcentagem de Atendimentos')
    ax.set_title(build_plot_title(con, params, 'Sexo'))
    ax.legend(wedges, x, title="Sexo")

    return fig

