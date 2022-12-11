import pandas as pd

#Automatic detection ROI
df_ROI_final = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/df_ROI_final.csv')

#Manual annotation ROI
df_annot_final = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/annot_new2.csv')

#Metafiles Xenocanto
df_metafiles_xenocanto = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/metafiles_xenocanto.csv')

#barycenter data
df_barycenter_biotope = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/barycenter_biotope.csv')

df_barycenter_biotope_family = pd.read_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/barycenter_biotope_family.csv')