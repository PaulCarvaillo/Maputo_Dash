#%%
from loaded_data import datasets_path
from glob import glob
from os.path import join

folder_names = glob(join(datasets_path,'wav'), recursive=True) 

print(folder_names)
# %%

