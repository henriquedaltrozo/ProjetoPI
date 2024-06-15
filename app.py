import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering

from flask import Flask, send_file, request
from sklearn.preprocessing import LabelEncoder
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
# > (barras) Quantidade de acidentes por ocupação (CBO)
# > (barras) Quantidade de acidentes por faixa-etaria
# > (pizza)  Quantidade de acidentes que resultaram em obito/não-obito
# > (pizza)  Quantidade de acidentes por sexo
# > (pizza)  Quantidade de acidentes urgentes/não-urgentes
# > (pontos) Quantidade de acidentes temporal
# > (pontos) Modelo preditivo na quantidade de acidentes temporal
# > Tabela de correlação

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

@app.route('/cor-mat')
def correlation_matrix_heatmap_api():
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
# ?tipo-localizacao=cidade/microregiao/estado
# ?localizacao=430010
#
# ?tipo-tempo=mes/semestre/ano
# ?tempo-ini=201802
# ?tempo-fim=202209
#
@app.route('/graficos/tipo-acidente')
def graphs_accident_type_api():
    var_type = request.args.get('tipo-var')
    var_type = var_type if var_type != None else 'quantidade'

    top = request.args.get('top')
    top = top if top != None else 5

    loc_type = request.args.get('tipo-localizacao')
    loc_type = loc_type if loc_type != None else 'estado'

    # loc = str(None)
    # if loc_type != 'estado':
    loc = request.args.get('localizacao')
    loc = loc if loc != None else '431020' # Default to Ijui

    # statement = '''
    # SELECT nome AS cid, ocorr 
    # FROM (
    #     SELECT pa_cidpri, COUNT(*) AS ocorr 
    #     FROM fato_pars 
    #     GROUP BY pa_cidpri
    # ) 
    # JOIN dim_cid ON id = pa_cidpri 
    # ORDER BY ocorr DESC 
    # LIMIT 5
    # '''

    loc_str = '' # Estado
    if loc_type == 'cidade':
        loc_str = 'WHERE pa_munpcn = ?'
    elif loc_type == 'microregiao':
        loc_str = 'JOIN dim_localizacao ON mun_id = pa_munpcn WHERE mic_id = ?'

    # TODO: Make function to generate dynamic statement
    statement = '''
    SELECT nome AS cid, apr 
    FROM (
        SELECT pa_cidpri, {} AS apr 
        FROM fato_pars 
        {}
        GROUP BY pa_cidpri
    ) 
    JOIN dim_cid ON id = pa_cidpri 
    ORDER BY apr DESC 
    LIMIT ?
    '''.format(
        'SUM(pa_valapr)' if var_type == 'valor' else 'COUNT(pa_qtdapr)',
        loc_str
    )

    # df = duckdb.sql(statement).df()
    con.execute(statement, [top] if loc_type == 'estado' else [loc, top])

    fig, ax = plt.subplots()

    result = con.fetchall()
    unzipped = list(zip(*result))
    x = [f'{str(i + 1)}°' for i in range(int(top))]
    y = list(unzipped[1])

    ax.bar(x, y, color=random_colors(int(top)), label=list(unzipped[0]))

    # TODO: Make generic to var_type and loc
    ax.set_ylabel('Número de Atendimentos')
    ax.set_title(f'{top} Principais Atendimentos por\nCategoria de Acidente na Cidade de {loc}')
    ax.legend(title='Categorias de Acidente')

    return send_plot()

