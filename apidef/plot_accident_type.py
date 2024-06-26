from apidef.util.custom_bar_plot import custom_bar_plot
from apidef.util.custom_plots import build_plot_title
import matplotlib.pyplot as plt
import duckdb

def build_accident_type_plot(con, params):
    fig, ax = plt.subplots()

    dim_cid = ('dim_cid', 'id', 'nome')
    custom_bar_plot(con, ax, params, dim_cid, 'pa_cidpri')

    ax.set_ylabel('Número de Atendimentos')
    ax.set_title(build_plot_title(con, params, 'Categoria de Acidente'))
    ax.legend(title='Categorias de Acidente')

    return fig

