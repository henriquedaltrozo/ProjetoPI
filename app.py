from apidef.table_statistical import build_statistical_table, build_statistical_table_other
from apidef.plot_temporal_prediction import build_temporal_prediction_plot
from apidef.plot_accident_type import build_accident_type_plot
from apidef.table_correlation import build_correlation_table
from apidef.plot_occupation import build_occupation_plot
from apidef.plot_temporal import build_temporal_plot
from apidef.plot_age import build_age_plot
from apidef.plot_sex import build_sex_plot
from flask import Flask, send_file, request
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib
import duckdb

# ==================================
# GRÁFICOS TODO
# =================================
# > XXX (barras) Quantidade de acidentes por tipo
#                http://localhost:5000/graficos/tipo-acidente
#
# > XXX (barras) Quantidade de acidentes por ocupação (CBO)
#                http://localhost:5000/graficos/ocupacao
#
# > XXX (barras) Quantidade de acidentes por faixa-etaria
#                http://localhost:5000/graficos/faixa-etaria
#
# > XXX (pizza)  Quantidade de acidentes por sexo
#                http://localhost:5000/graficos/sexo
#
# > (pontos) Quantidade de acidentes temporal
#                http://localhost:5000/graficos/temporal
#
# > (pontos) Modelo preditivo na quantidade de acidentes temporal
#                http://localhost:5000/predicoes/temporal
#
# > (tabela) Com porcentagens de meta indicando se a região escolhida está
#            acima ou abaixo da média proporcional de outra região e tals
#                http://localhost:5000/tabelas/comparacao
#
# > (tabela) Tabela de correlação
#                http://localhost:5000/tabelas/correlacao

# con = duckdb.connect('database.db')
# print(con.sql('SHOW TABLES'))

matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering

app = Flask(__name__)

# con.close()

def send_fig(fig):
    # Save it to a BytesIO object
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    plt.close(fig)

    # Return the fig as a response
    return send_file(buf, mimetype='image/png')

def extract_request_params():
    var_type = request.args.get('tipo-var')
    var_type = var_type if var_type != None else 'quantidade'

    top = request.args.get('top')
    top = top if top != None else 5

    loc_type = request.args.get('tipo-localizacao')
    loc_type = loc_type if loc_type != None else 'estado'

    loc = request.args.get('localizacao')
    loc = loc if loc != None else '431020' # Default to Ijui

    return var_type, top, loc_type, loc

# def build_plot_sql_statement(params, ???):

@app.route('/cities')
def cities_api():
    con = duckdb.connect('database.db')

    con.execute('SELECT codigo, descr FROM rs_municip')
    cities = con.fetchall()

    # Remove code from city name
    cities = [
        (city[0], city[1][7:] if i > 0 else city[1]) 
        for i, city in enumerate(cities)
    ]

    return { key: value for key, value in cities }

@app.route('/tabelas/correlacao')
def correlation_table_api():
    con = duckdb.connect('database.db')
    params = extract_request_params()

    fig = build_correlation_table(con, params)

    return send_fig(fig)

@app.route('/tabelas/comparacao')
def statistical_table_api():
    con = duckdb.connect('database.db')
    # params = extract_request_params()

    fig = build_statistical_table(con)

    return send_fig(fig)

@app.route('/tabelas/comparacao_outro')
def statistical_table_other_api():
    con = duckdb.connect('database.db')
    # params = extract_request_params()

    fig = build_statistical_table_other(con)

    return send_fig(fig)

# http://localhost/graficos/tipo-acidente?var=quantidade?city=430010?tempo=semestre?tempo-ini=202103?tempo-fim=202208
#
# ?tipo-var=quantidade/valor
#
# ?top=5
#
# ?tipo-localizacao=cidade/microrregiao/estado
# ?localizacao=430010
#
# ?tipo-tempo=mes/semestre/ano
# ?tempo-ini=201802
# ?tempo-fim=202209
#
@app.route('/graficos/tipo-acidente')
def accident_type_plot_api():
    con = duckdb.connect('database.db')
    params = extract_request_params()

    fig = build_accident_type_plot(con, params)

    return send_fig(fig)

@app.route('/graficos/ocupacao')
def occupation_plot_api():
    con = duckdb.connect('database.db')
    params = extract_request_params()

    fig = build_occupation_plot(con, params)

    return send_fig(fig)

@app.route('/graficos/faixa-etaria')
def age_plot_api():
    con = duckdb.connect('database.db')
    params = extract_request_params()

    fig = build_age_plot(con, params)

    return send_fig(fig)

@app.route('/graficos/sexo')
def sex_plot_api():
    con = duckdb.connect('database.db')
    params = extract_request_params()

    fig = build_sex_plot(con, params)

    return send_fig(fig)

@app.route('/graficos/temporal')
def temporal_plot_api():
    con = duckdb.connect('database.db')
    params = extract_request_params()

    fig = build_temporal_plot(con, params)

    return send_fig(fig)

@app.route('/predicao/acidentes')
def temporal_prediction_plot_api():
    con = duckdb.connect('database.db')
    # params = extract_request_params()

    fig = build_temporal_prediction_plot(con)

    return send_fig(fig)

