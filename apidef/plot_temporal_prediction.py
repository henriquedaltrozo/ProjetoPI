from apidef.util.custom_plots import build_plot_title
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import duckdb

def build_temporal_prediction_plot(con, params):
    ax, fig = plt.subplots()
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
    return fig

