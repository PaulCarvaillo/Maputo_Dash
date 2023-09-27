from os.path import join, dirname
import pandas as pd

tables_path = join(dirname(dirname(__file__)), 'datasets', 'tables')

df_ROI_final = pd.read_csv(join(tables_path, 'df_ROI_final.csv'))
df_annot_final = pd.read_csv(join(
    tables_path, 'annot_new2.csv'))  # Manual annotation ROI

df_metafiles_xenocanto = pd.read_csv(
    join(tables_path, 'metafiles_xenocanto.csv'))

# For MOBI presentation demo and report:
df_barycenter_biotope = pd.read_csv(
    join(tables_path, 'barycenter_biotope.csv'))
df_barycenter_biotope_family = pd.read_csv(
    join(tables_path, 'barycenter_biotope_family.csv'))
