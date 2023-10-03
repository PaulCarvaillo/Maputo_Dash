# In this notebook, we explore Region of interest detection using scikit-maad
import librosa
import maad
import numpy as np
import pandas as pd
import soundfile as sf
from maad import rois, sound, util
from maad.features import all_shape_features, centroid_features
from maad.util import format_features, power2dB

from assets.features import SPECTRAL_FEATURES, TEMPORAL_FEATURES


def find_ROIs_soundfile(
    path="",
    display=False,
    mode_bin="relative",
    param1=10,
    param2=0.9,
    fmin=100,
    fmax=15000,
):
    # workaround RIFF bug from xenocanto import TODO
    temp, sr = librosa.load(path)
    sf.write("tmp.wav", temp, 44100)

    dB_max = 96
    s, fs = maad.sound.load("tmp.wav")

    maxAmp = np.abs(s).max()
    Sxx_power, tn, fn, ext = maad.sound.spectrogram(
        s / maxAmp, fs, flims=(fmin, fmax), display=False
    )
    Sxx_db = maad.util.power2dB(Sxx_power) + dB_max
    Sxx_power_noNoise = sound.median_equalizer(
        Sxx_power, display=False, **{"extent": ext}
    )
    Sxx_db_noNoise = power2dB(Sxx_power_noNoise)
    Sxx_db_noNoise_smooth = sound.smooth(
        Sxx_db_noNoise,
        std=0.5,
        display=False,
        savefig=None,
        **{"vmin": 0, "vmax": dB_max, "extent": ext}
    )

    im_mask = rois.create_mask(
        im=Sxx_db_noNoise_smooth,
        mode_bin="relative",
        bin_std=param1,
        bin_per=param2,
        verbose=False,
        display=False,
    )

    im_rois, df_rois = rois.select_rois(
        im_mask,
        min_roi=25,
        max_roi=None,
        display=display,
        **{"extent": ext, "figsize": (4, 13)}
    )

    df_rois = format_features(df_rois, tn, fn)
    im_zeros = np.zeros(Sxx_db.shape)
    im_blobs = rois.rois_to_imblobs(im_zeros, df_rois)
    only_blobs = im_blobs * Sxx_db

    if display:
        fig_kwargs = {
            "vmax": Sxx_db.max(),
            "vmin": -20,
            "extent": ext,
            "figsize": (4, 13),
            "xlabel": "Time [sec]",
            "ylabel": "Frequency [Hz]",
        }
        fig, ax = maad.util.plot2d(
            Sxx_db, title="Power spectrogram density (PSD)", **fig_kwargs
        )
        fig, ax = maad.util.plot2d(
            Sxx_db_noNoise,
            title="Power spectrogram density (PSD)_NoNoise",
            **fig_kwargs
        )
        fig, ax = maad.util.plot2d(
            Sxx_db_noNoise_smooth,
            title="Power spectrogram density (PSD)_NoNoise +smooth",
            **fig_kwargs
        )
        util.plot2d(only_blobs)

    return df_rois, s, fs, fig, ax


def compute_ROI_all_features(s, fs, df_rois, resolution="med", display=True):
    df_rois_shape = all_shape_features(
        s, fs, df_rois, resolution=resolution, display=display
    )

    df_temporal_features = pd.DataFrame(columns=TEMPORAL_FEATURES)
    df_spectral_features = pd.DataFrame(columns=SPECTRAL_FEATURES)

    # Loop
    for index, row in df_rois.iloc[1:].iterrows():
        s_trim = sound.trim(s, fs, row.loc[index, "min_t"], row.loc[index, "max_t"])
        s_trim = s_trim - np.mean(s_trim)
        s_trim = s_trim / np.max(np.abs(s_trim))
        Sxx_trim_power, tn, fn, ext = sound.spectrogram(
            s_trim, fs, verbose=False, display=False, savefig=None
        )

        spectral_features_temp, _ = maad.features.all_spectral_alpha_indices(
            Sxx_trim_power, tn, fn, display=False
        )
        df_spectral_features = df_spectral_features.append(
            spectral_features_temp, ignore_index=True
        )
        temp = maad.features.all_temporal_alpha_indices(s_trim, fs)
        df_temporal_features = df_temporal_features.append(temp, ignore_index=True)

    df_rois_all_features = pd.concat(
        [df_rois_shape, df_spectral_features, df_temporal_features], axis=1
    )

    return df_rois_all_features


def compute_Sxx_dB_nonoise_smooth(path="", fmin=100, fmax=10000, smoothing=0.5):
    # workaround RIFF bug from xenocanto import TODO
    temp, sr = librosa.load(path, sr=None)
    sf.write("tmp.wav", temp, sr)

    dB_max = 96
    s, fs = maad.sound.load("tmp.wav")
    maxAmp = np.abs(s).max()  # used to normalize
    Sxx_power, tn, fn, ext = maad.sound.spectrogram(
        s / maxAmp, fs, flims=(fmin, fmax), display=False
    )

    Sxx_power_noNoise = sound.median_equalizer(
        Sxx_power, display=False, **{"extent": ext}
    )
    Sxx_db_noNoise = power2dB(Sxx_power_noNoise)
    Sxx_db_noNoise_smooth = sound.smooth(
        Sxx_db_noNoise,
        std=smoothing,
        display=False,
        savefig=None,
        **{"vmin": 0, "vmax": dB_max, "extent": ext}
    )
    return Sxx_db_noNoise_smooth, tn, fn, ext


def ROI_and_centroid(
    Sxx_db_noNoise_smooth,
    tn,
    fn,
    ext,
    mode_bin="relative",
    param1=18,
    param2=0.7,
    display=False,
):
    im_mask = rois.create_mask(
        im=Sxx_db_noNoise_smooth,
        mode_bin=mode_bin,
        bin_std=param1,
        bin_per=param2,
        verbose=False,
        display=False,
    )

    im_rois, df_rois = rois.select_rois(
        im_mask,
        min_roi=25,
        max_roi=None,
        display=display,
        **{"extent": ext, "figsize": (4, 13)}
    )

    df_rois = format_features(df_rois, tn, fn)

    centroid = format_features(
        centroid_features(Sxx_db_noNoise_smooth, df_rois), tn, fn
    )

    return im_rois, df_rois, centroid
