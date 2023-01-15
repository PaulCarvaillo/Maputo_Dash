import pandas as pd
import os
import os
import requests
from tqdm import tqdm

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
            