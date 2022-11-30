# imports
import pandas as pd
# import processed data from datasets
df_metafiles_xenocanto = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/metafiles_xenocanto.csv')
df_metafiles_xenocanto_reduced = df_metafiles_xenocanto.loc[:, [
    'id', 'gen','rec','loc', 'sp', 'lat', 'lng', 'alt', 'type', 'q', 'length', 'bird-seen']]

