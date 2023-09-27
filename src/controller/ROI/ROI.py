# In this notebook, we explore Region of interest detection using scikit-maad
import librosa
import maad
import numpy as np
import pandas as pd
import soundfile as sf
from maad import rois, sound, util
from maad.features import all_shape_features, centroid_features
from maad.util import format_features, power2dB


def find_ROIs_soundfile(
    path="",
    display=False,
    mode_bin="relative",
    param1=10,
    param2=0.9,
    fmin=100,
    fmax=15000,
):
    """Finds ROIs in a .wav file. param1 and param2

    mode_bin : string in {'relative', 'absolute'}, optional, default is 'relative'
        if 'absolute' [1]_ , a double threshold with absolute value is performed
        with two parameters (see \*\*kwargs section)
        if 'relative' [2]_, a relative double threshold is performed with two
        parameters (see \*\*kwargs section)

        Param1 and 2:
     if 'absolute' [1]_
        - bin_h : scalar, optional, default is 0.7
        Set the first threshold. Value higher than this value are set to 1,
        the others are set to 0. They are the seeds for the second step
        - bin_l: scalar, optional, defautl is 0.2
        Set the second threshold. Value higher than this value and connected
        to the seeds or to other pixels connected to the seeds (6-connectivity)
        are set to 1, the other remains 0

        if 'relative' [2]_ :
        - bin_std :  scalar, optional, default is 6
        bin_std is needed to compute the threshold1.
        This threshold is not an absolute value but depends on values that are
        similar to 75th percentile (pseudo_mean) and a sort of std value of
        the image.
        threshold1 = "pseudo_mean" + "std" * bin_std
        Value higher than threshold1 are set to 1, they are the seeds for
        the second step. The others are set to 0.
        - bin_per: scalar, optional, defautl is 0.5
        Set how much the second threshold is lower than the first
        threshold value. From 0 to 1. ex: 0.1 = 10 %.
        threshold2 = threshold1 (1-bin_per)
        Value higher than threshold2 and connected (6-connectivity) to the
        seeds are set to 1, the other remains 0

    """
    # workaround RIFF bug from xenocanto import TO BE CHANGED
    temp, sr = librosa.load(path)
    sf.write("tmp.wav", temp, 44100)

    # Load using Maad, compute spectro
    dB_max = 96
    s, fs = maad.sound.load("tmp.wav")

    maxAmp = np.abs(s).max()  # used to normalize
    Sxx_power, tn, fn, ext = maad.sound.spectrogram(
        s / maxAmp, fs, flims=(fmin, fmax), display=False
    )
    Sxx_db = maad.util.power2dB(Sxx_power) + dB_max
    # Denoise it
    # First we remove the stationary background using median equalizer in order to increase the contrast [1]
    Sxx_power_noNoise = sound.median_equalizer(
        Sxx_power, display=False, **{"extent": ext}
    )
    Sxx_db_noNoise = power2dB(Sxx_power_noNoise)
    # Then we smooth the spectrogram in order to facilitate the creation of masks as
    # small sparse details are merged if they are close to each other
    Sxx_db_noNoise_smooth = sound.smooth(
        Sxx_db_noNoise,
        std=0.5,
        display=False,
        savefig=None,
        **{"vmin": 0, "vmax": dB_max, "extent": ext}
    )

    # Then we create a mask (i.e. binarization of the spectrogram) by using the
    # double thresholding technique
    im_mask = rois.create_mask(
        im=Sxx_db_noNoise_smooth,
        mode_bin="relative",
        bin_std=param1,
        bin_per=param2,
        verbose=False,
        display=False,
    )

    # Finaly, we put together pixels that belong to the same acoustic event, and
    # remove very small events (<=25 pixel²)
    im_rois, df_rois = rois.select_rois(
        im_mask,
        min_roi=25,
        max_roi=None,
        display=display,
        **{"extent": ext, "figsize": (4, 13)}
    )

    # format dataframe df_rois in order to convert pixels into time and frequency
    df_rois = format_features(df_rois, tn, fn)
    im_zeros = np.zeros(Sxx_db.shape)
    im_blobs = rois.rois_to_imblobs(im_zeros, df_rois)
    only_blobs = im_blobs * Sxx_db

    if display:
        # Plot spectrograms to see Denoising and smoothing process
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
    # compute features using MAAD
    df_rois_shape = all_shape_features(
        s, fs, df_rois, resolution=resolution, display=display
    )
    # # Filter those that we understand

    # COMPUTE MAAD SPECTRAL AND TEMPORAL ALPHA FEATURES ON EACH ROI
    SPECTRAL_FEATURES = [
        "MEANf",
        "VARf",
        "SKEWf",
        "KURTf",
        "NBPEAKS",
        "LEQf",
        "ENRf",
        "BGNf",
        "SNRf",
        "Hf",
        "EAS",
        "ECU",
        "ECV",
        "EPS",
        "EPS_KURT",
        "EPS_SKEW",
        "ACI",
        "NDSI",
        "rBA",
        "AnthroEnergy",
        "BioEnergy",
        "BI",
        "ROU",
        "ADI",
        "AEI",
        "LFC",
        "MFC",
        "HFC",
        "ACTspFract",
        "ACTspCount",
        "ACTspMean",
        "EVNspFract",
        "EVNspMean",
        "EVNspCount",
        "TFSD",
        "H_Havrda",
        "H_Renyi",
        "H_pairedShannon",
        "H_gamma",
        "H_GiniSimpson",
        "RAOQ",
        "AGI",
        "ROItotal",
        "ROIcover",
    ]

    TEMPORAL_FEATURES = [
        "ZCR",
        "MEANt",
        "VARt",
        "SKEWt",
        "KURTt",
        "LEQt",
        "BGNt",
        "SNRt",
        "MED",
        "Ht",
        "ACTtFraction",
        "ACTtCount",
        "ACTtMean",
        "EVNtFraction",
        "EVNtMean",
        "EVNtCount",
    ]

    df_temporal_features = pd.DataFrame(columns=TEMPORAL_FEATURES)
    df_spectral_features = pd.DataFrame(columns=SPECTRAL_FEATURES)

    # Loop
    for index, row in df_rois.iloc[1:].iterrows():
        # trim sound to process only portion of the sound that correspond
        # to the current ROI
        s_trim = sound.trim(s, fs, row.loc[index, "min_t"], row.loc[index, "max_t"])
        s_trim = s_trim - np.mean(s_trim)
        s_trim = s_trim / np.max(np.abs(s_trim))

        # compute spectral alpha indices for each ROI
        Sxx_trim_power, tn, fn, ext = sound.spectrogram(
            s_trim, fs, verbose=False, display=False, savefig=None
        )

        spectral_features_temp, _ = maad.features.all_spectral_alpha_indices(
            Sxx_trim_power, tn, fn, display=False
        )
        df_spectral_features = df_spectral_features.append(
            spectral_features_temp, ignore_index=True
        )

        # compute temporal alpha indices for each ROI
        temp = maad.features.all_temporal_alpha_indices(s_trim, fs)
        df_temporal_features = df_temporal_features.append(temp, ignore_index=True)

    df_rois_all_features = pd.concat(
        [df_rois_shape, df_spectral_features, df_temporal_features], axis=1
    )

    return df_rois_all_features


def compute_Sxx_dB_nonoise_smooth(path="", fmin=100, fmax=10000, smoothing=0.5):
    # workaround RIFF bug from xenocanto import TO BE CHANGED
    temp, sr = librosa.load(path, sr=None)
    sf.write("tmp.wav", temp, sr)

    # Load using Maad, compute spectro
    dB_max = 96
    s, fs = maad.sound.load("tmp.wav")
    maxAmp = np.abs(s).max()  # used to normalize
    Sxx_power, tn, fn, ext = maad.sound.spectrogram(
        s / maxAmp, fs, flims=(fmin, fmax), display=False
    )
    # Sxx_db = maad.util.power2dB(Sxx_power) + dB_max
    # Denoise it
    # First we remove the stationary background using median equalizer in order to increase the contrast [1]
    Sxx_power_noNoise = sound.median_equalizer(
        Sxx_power, display=False, **{"extent": ext}
    )
    Sxx_db_noNoise = power2dB(Sxx_power_noNoise)
    # Then we smooth the spectrogram in order to facilitate the creation of masks as
    # small sparse details are merged if they are close to each other
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
    # Then we create a mask (i.e. binarization of the spectrogram) by using the
    # double thresholding technique
    im_mask = rois.create_mask(
        im=Sxx_db_noNoise_smooth,
        mode_bin=mode_bin,
        bin_std=param1,
        bin_per=param2,
        verbose=False,
        display=False,
    )

    # Finaly, we put together pixels that belong to the same acoustic event, and
    # remove very small events (<=25 pixel²)
    im_rois, df_rois = rois.select_rois(
        im_mask,
        min_roi=25,
        max_roi=None,
        display=display,
        **{"extent": ext, "figsize": (4, 13)}
    )

    # format dataframe df_rois in order to convert pixels into time and frequency
    df_rois = format_features(df_rois, tn, fn)

    # Compute centroid features
    centroid = format_features(
        centroid_features(Sxx_db_noNoise_smooth, df_rois), tn, fn
    )

    return im_rois, df_rois, centroid
