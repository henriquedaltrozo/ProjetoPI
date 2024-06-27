import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering

from flask import Flask, send_file, request
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import duckdb
import numpy as np
import pandas as pd
from random import randint

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

con = duckdb.connect('database.db')
# print(con.sql('SHOW TABLES'))

app = Flask(__name__)

# con.close()

def send_plot():
    # Save it to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Return the plot as a response
    return send_file(buf, mimetype='image/png')

def random_colors(n):
    r = np.random.rand(n)
    g = np.random.rand(n)
    b = np.random.rand(n)

    return list(zip(r, g, b))

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

city_names = {}
def get_city_name(loc):
    global city_names

    # If city_names is empty, populate it from the database
    if (not city_names):
        con.execute('SELECT mun_id, mun_nome FROM dim_localizacao')
        city_names = { str(id): name.title() for id, name in con.fetchall() }

    return city_names[loc]

def build_plot_title(params, topic):
    var_type, top, loc_type, loc = params

    city_name = get_city_name(loc)

    loc_str_ = ''
    if loc_type == 'cidade':
        loc_str = f'na Cidade de {city_name} - RS'
    elif loc_type == 'microrregiao':
        loc_str = f'na Microrregião de {city_name} - RS'
    elif loc_type == 'estado':
        loc_str = f'no Estado do Rio Grande do Sul'

    title = f'''
    Quantidade de Atendimentos Relacionados a Acidentes
    de Trânsito por {topic} {loc_str}'''

    return title

# def build_plot_sql_statement(params, ???):

def get_loc_sql(loc_type, loc):
    loc_sql = '' # Estado
    if loc_type == 'cidade':
        loc_sql = f'WHERE pa_munpcn = {loc}'
    elif loc_type == 'microrregiao':
        loc_sql = f'JOIN dim_localizacao ON mun_id = pa_munpcn WHERE mic_id = {loc}'

    return loc_sql

# def get_loc_text(loc_type, loc):

def get_qtd_val_sql(var_type):
    return 'SUM(pa_valapr)' if var_type == 'valor' else 'COUNT(pa_qtdapr)'

def custom_bar_plot_statement(ax, top, statement):
    # var_type, top, loc_type, loc = params

    # df = duckdb.sql(statement).df()
    con.execute(statement)

    result = con.fetchall()
    unzipped = list(zip(*result))
    x = [f'{str(i + 1)}°' for i in range(int(top))]
    y = list(unzipped[1])

    ax.bar(x, y, color=random_colors(int(top)), label=list(unzipped[0]))

def custom_bar_plot(ax, params, dim, x, group_by=None, join_inside=False):
    var_type, top, loc_type, loc = params

    loc_sql = get_loc_sql(loc_type, loc)
    qtd_val_sql = get_qtd_val_sql(var_type)

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
    
    custom_bar_plot_statement(ax, top, statement)

@app.route('/')
def hello_world():
    return '<p>Hello, World!</p>'

@app.route('/cities')
def cities_api():
    con.execute('SELECT codigo, descr FROM rs_municip')
    cities = con.fetchall()

    # Remove code from city name
    cities = [
        (city[0], city[1][7:] if i > 0 else city[1]) 
        for i, city in enumerate(cities)
    ]

    return { key: value for key, value in cities }

@app.route('/tabelas/correlacao')
def correlation_matrix_heatmap_api():
    # df = con.execute('SELECT * FROM fato_pars').df()
    df = con.execute('SELECT * FROM fato_pars').df()

    # Columns that are not numeric
    categorical_cols = df.select_dtypes(include=['object']).columns

    # Convert them to numeric
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le # Save the encoding to reverse later

    # Clear NULLs
    drop_columns = [
        'pa_incout', 'pa_incurg', 'pa_tippre', 'pa_subfin', 'pa_docorig', 
        'pa_motsai', 'pa_obito', 'pa_encerr', 'pa_perman', 'pa_alta', 'pa_transf',
        'pa_cidsec', 'pa_cidcas', 'pa_dif_val', 'pa_fler', 'pa_vl_cf'
    ]
    df = df.drop(columns=drop_columns) 

    # corr = df[df.columns[:10]].corr()
    corr = df.corr()

    # Mask to get only one half of the heatmap
    mask = np.triu(np.ones_like(corr, dtype=bool))

    # Draw heatmap
    plt.figure(figsize=(30,18)) # (22, 16)
    heatmap = sns.heatmap(corr, vmin=-1, vmax=1, fmt='.2f', 
        mask=mask, annot=True, cmap='BrBG')
    heatmap.set_title('Matriz de Correlação', fontdict={'fontsize':10}, pad=12)
    
    return send_plot()

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
def graphs_accident_type_api():
    fig, ax = plt.subplots()

    params = extract_request_params()
    dim_cid = ('dim_cid', 'id', 'nome')
    custom_bar_plot(ax, params, dim_cid, 'pa_cidpri')

    ax.set_ylabel('Número de Atendimentos')
    ax.set_title(build_plot_title(params, 'Categoria de Acidente'))
    ax.legend(title='Categorias de Acidente')

    return send_plot()

@app.route('/graficos/ocupacao')
def graphs_ocupation_api():
    fig, ax = plt.subplots()

    params = extract_request_params()
    dim_ocupacao = ('dim_ocupacao', 'id', 'nome')
    custom_bar_plot(ax, params, dim_ocupacao, 'pa_cbocod')

    ax.set_ylabel('Número de Atendimentos')
    ax.set_title(build_plot_title(params, 'Ocupação do Profissional da Saúde'))
    ax.legend(title='Ocupação')

    return send_plot()

@app.route('/graficos/faixa-etaria')
def graphs_age_api():
    fig, ax = plt.subplots()

    params = extract_request_params()
    dim_idade = ('dim_idade', 'idade', 'faixa_etaria')
    custom_bar_plot(ax, params, dim_idade, 'pa_idade', 'faixa_etaria', True)

    ax.set_ylabel('Número de Atendimentos')
    ax.set_title(build_plot_title(params, 'Faixa-Etária'))
    ax.legend(title='Faixa-etária')

    return send_plot()

@app.route('/graficos/sexo')
def graphs_sex_api():
    fig, ax = plt.subplots()

    params = extract_request_params()
    var_type, top, loc_type, loc = params

    loc_sql = get_loc_sql(loc_type, loc)
    qtd_val_sql = get_qtd_val_sql(var_type)

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

    wedges, texts, autotexts = ax.pie(y, 
        autopct=lambda val: f'{val:.1f}%', 
        colors=['cornflowerblue', 'hotpink'],
        textprops=dict(color="w"))

    ax.set_xlabel('Porcentagem de Atendimentos')
    ax.set_title(build_plot_title(params, 'Sexo'))
    ax.legend(wedges, x, title="Sexo")

    return send_plot()

@app.route('/predicao/acidentes')
def predict_accidents():
    statement = '''
    SELECT ano, COUNT(*) AS total_acidentes 
    FROM fato_pars 
    JOIN dim_tempo ON pa_cmp = id 
    GROUP BY ano 
    ORDER BY ano
    '''
    df = con.execute(statement).df()
    X = df[['ano']]
    y = df['total_acidentes']
    model = LinearRegression()
    model.fit(X, y)
    future_years = pd.DataFrame({'ano': range(X['ano'].max() + 1, X['ano'].max() + 6)})
    predictions = model.predict(future_years)
    plt.figure(figsize=(10, 6))
    plt.plot(df['ano'], df['total_acidentes'], label='Dados Reais', marker='o')
    plt.plot(future_years['ano'], predictions, label='Previsões', linestyle='--', marker='x')
    plt.xlabel('Ano')
    plt.ylabel('Número de Acidentes')
    plt.title('Previsão de Acidentes Futuros')
    plt.legend()
    return send_plot()
