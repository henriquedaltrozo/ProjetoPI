from apidef.util.custom_plots import custom_bar_plot, build_plot_title
import matplotlib.pyplot as plt
import duckdb

def build_occupation_plot(con, params):
    fig, ax = plt.subplots()

    dim_ocupacao = ('dim_ocupacao', 'id', 'nome')
    custom_bar_plot(con, ax, params, dim_ocupacao, 'pa_cbocod')

    ax.set_ylabel('Número de Atendimentos')
    ax.set_title(build_plot_title(con, params, 'Ocupação do Profissional da Saúde'))
    ax.legend(title='Ocupação')

    return fig

