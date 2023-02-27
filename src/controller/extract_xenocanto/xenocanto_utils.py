import pandas as pd
import os
import os
import requests
from tqdm import tqdm
from glob import glob
from pathlib import Path


def download_files(df_recordings, root_dir='.', overwrite=True):
    for index, row in df_recordings.iterrows():
        directory = os.path.join(root_dir, row["gen"] + '_' + row["sp"])
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, str(row["id"]) + '.wav')
        if os.path.exists(file_path) and not overwrite:
            continue
        try:
            response = requests.get(row["file"], stream=True, timeout=5)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                total_size = int(response.headers.get("content-length", 0))
                for data in tqdm(response.iter_content(1024), total=total_size, unit='B', unit_scale=True, desc=file_path, leave=False):
                    f.write(data)
        except (requests.exceptions.RequestException, IOError) as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            print("An error occurred while processing: " + row["file"])
            print("Error: ", e)

    filelist = glob(root_dir+'/**/*.wav', recursive=True)
    df_data = pd.DataFrame()
    for file in filelist:
        species = Path(file).parts[-2].rsplit(sep='_')[1]
        gen = Path(file).parts[-2].rsplit(sep='_')[0]
        df_data = df_data.append({'fullfilename': file,
                                  'sound_id': Path(file).parts[-1][:-4],
                                  'species': species,
                                  'gen': gen},
                                 ignore_index=True)

    # df_data.to_csv(os.path.join(os.path(root_dir)[
    #     :-1], 'tables', 'df_soundfiles_paths.csv'))
    df_data.to_csv(
        '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/COUA_TEST/tables/df_soundfiles_paths.csv')
