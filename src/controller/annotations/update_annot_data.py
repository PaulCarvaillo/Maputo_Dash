
import pandas as pd
from glob import glob
from pathlib import Path
import maad
import librosa
import soundfile as sf
import numpy as np

# convert excel to csv
df_annot_excel = pd.read_excel(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/annot1.xlsx', 1)
df_annot_excel.to_csv(
    '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/annot1.csv')


def get_and_clean_new_annot_data():
    datapath = '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/wav/xenocanto'
    annot_path = '/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/Maputo_Dash/datasets/tables/annot1.csv'

    filelist = glob(datapath+'/**/*.wav', recursive=True)
    df_data = pd.DataFrame()
    for file in filelist:
        species = Path(file).parts[-2].rsplit(sep='_')[1]
        gen = Path(file).parts[-2].rsplit(sep='_')[0]
        df_data = df_data.append({'fullfilename': file,
                                  'sound_id': Path(file).parts[-1][:-4],
                                  'species': species,
                                  'gen': gen},
                                 ignore_index=True)

    df_annot = pd.read_csv(annot_path)
    df_annot['sound_id'] = df_annot['record'].astype(str)
    # filter annotations to .wav files we have in datasets/xenocanto/ (in case someone lost a wav file or an annotation)
    df_annot = df_annot[df_annot.sound_id.isin(df_data.sound_id)]

    # COMPUTE MAAD SPECTRAL AND TEMPORAL ALPHA FEATURES ON EACH OF THE MANNUALLY CONTOURED ROI
    # list of features computed by maad, we filter them out later and compute them anyway....
    SPECTRAL_FEATURES = ['MEANf', 'VARf', 'SKEWf', 'KURTf', 'NBPEAKS', 'LEQf',
                         'ENRf', 'BGNf', 'SNRf', 'Hf', 'EAS', 'ECU', 'ECV', 'EPS', 'EPS_KURT', 'EPS_SKEW', 'ACI',
                         'NDSI', 'rBA', 'AnthroEnergy', 'BioEnergy', 'BI', 'ROU', 'ADI', 'AEI', 'LFC', 'MFC', 'HFC',
                         'ACTspFract', 'ACTspCount', 'ACTspMean', 'EVNspFract', 'EVNspMean', 'EVNspCount',
                         'TFSD', 'H_Havrda', 'H_Renyi', 'H_pairedShannon', 'H_gamma', 'H_GiniSimpson', 'RAOQ',
                         'AGI', 'ROItotal', 'ROIcover']

    TEMPORAL_FEATURES = ['ZCR', 'MEANt', 'VARt', 'SKEWt', 'KURTt',
                         'LEQt', 'BGNt', 'SNRt', 'MED', 'Ht', 'ACTtFraction', 'ACTtCount',
                         'ACTtMean', 'EVNtFraction', 'EVNtMean', 'EVNtCount']

    df_annot_final = pd.DataFrame()
    i = 1
    for file in filelist[:2]:
        print(f'loading ({i}/{len(filelist)}): {file}...')
        i += 1
        #load .wav
        temp, sr = librosa.load(file, sr=None)
        sf.write('tmp.wav', temp, sr)
        s, fs = maad.sound.load('tmp.wav')
        maxAmp = np.abs(s).max()  # used to normalize
        # get spectro for tn and fn
        Sxx_power, tn, fn, ext = maad.sound.spectrogram(
            s/maxAmp, fs, flims=(0, 20000), display=False)

        # get ROI from annotation and convert x y to t f
        df_roi_annot = df_annot[df_annot['sound_id'] == Path(
            file).parts[-1][:-4]].reset_index(drop=True)
        df_roi_annot = maad.util.format_features(df_roi_annot, tn, fn)

        # if soundfile is anotated
        if len(df_roi_annot) > 0:
            # compute all shape features
            df_rois_shape_temp = maad.features.all_shape_features(
                s, fs, df_roi_annot, resolution='med', display=False)
            df_rois_shape = df_rois_shape.append(
                df_rois_shape_temp.reset_index(drop=True), ignore_index=True)

            # compute all spectral and temporal features
            df_temporal_features = pd.DataFrame(columns=TEMPORAL_FEATURES)
            df_spectral_features = pd.DataFrame(columns=SPECTRAL_FEATURES)
            for index, row in df_roi_annot.iloc[0:].iterrows():
                df_rois_all_features_temp = pd.DataFrame()
                s_trim = maad.sound.trim(
                    s, fs, row.min_t, row.max_t)
                s_trim = (s_trim - np.mean(s_trim)) / (np.max(np.abs(s_trim)))
                try:
                    Sxx_trim_power, tn, fn, ext = maad.sound.spectrogram(s_trim, fs,
                                                                         verbose=False, display=False,
                                                                         savefig=None)
                    spectral_features_temp, _ = maad.features.all_spectral_alpha_indices(
                        Sxx_trim_power, tn, fn, display=False)

                    temporal_features_temp = maad.features.all_temporal_alpha_indices(
                        s_trim, fs)
                except:
                    print(str(file)+': error at index (chunk too small?): '+str(index) +
                          '\n s_trim looks like:'+str(s_trim.shape)+'\n temporal size:'+str(row.min_t - row.max_t))
                df_spectral_features = df_spectral_features.append(
                    spectral_features_temp, ignore_index=True)
                df_temporal_features = df_temporal_features.append(
                    temporal_features_temp, ignore_index=True)

                df_rois_all_features_temp['ID'] = Path(file).parts[-1][:-4]
                df_rois_all_features_temp = pd.concat(
                    [df_spectral_features, df_temporal_features], axis=1).reset_index(drop=True)

            df_annot_final = pd.concat(
                [df_annot_final, df_rois_all_features_temp, df_rois_shape], axis=0)
        else:
            print('no annotation available')
            pass
    return df_annot_final, df_rois_shape_temp

# %%
