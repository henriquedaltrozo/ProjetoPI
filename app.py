import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering

from flask import Flask, send_file, request
from io import BytesIO
import matplotlib.pyplot as plt
import duckdb
import numpy as np
from random import randint

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

