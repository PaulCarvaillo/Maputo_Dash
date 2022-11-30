import pandas as pd
from xenopy import Query


def extract_country_sounds_from_xenocanto(cnt="Mozambique", download=False, output_dir='/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/BioSoundTutorial-master/datasets/xenocanto/wav'):
    q = Query(cnt=cnt, type='call', q='A')
    metafiles = q.retrieve_meta(verbose=True)
    df_metafiles = pd.DataFrame(metafiles['recordings'])
    # retrieve recordings
    if download == True:
        q.retrieve_recordings(multiprocess=True, nproc=10,
                              attempts=10, outdir=output_dir)

    return df_metafiles

