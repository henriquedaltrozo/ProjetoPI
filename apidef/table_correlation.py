from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import duckdb

def build_correlation_table(con, params):
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

    fig, ax = plt.subplots(figsize=(30,18))

    # Draw heatmap
    # plt.figure(figsize=(30,18)) # (22, 16)
    heatmap = sns.heatmap(corr, vmin=-1, vmax=1, fmt='.2f', 
        mask=mask, annot=True, cmap='BrBG', ax=ax)
    heatmap.set_title('Matriz de Correlação', fontdict={'fontsize':10}, pad=12)

    return fig

