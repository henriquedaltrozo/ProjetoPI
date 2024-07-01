from apidef.util.custom_bar_plot import custom_bar_plot
from apidef.util.custom_plots import build_plot_title
import matplotlib.pyplot as plt
import duckdb

def build_age_plot(con, params):
    fig, ax = plt.subplots()

    dim_idade = ('dim_idade', 'idade', 'faixa_etaria')
    custom_bar_plot(con, ax, params, dim_idade, 'pa_idade', 'faixa_etaria', True)

    ax.set_ylabel('Número de Atendimentos')
    ax.set_title(build_plot_title(con, params, 'Faixa-Etária'))
    ax.legend(title='Faixa-etária')

    return fig

