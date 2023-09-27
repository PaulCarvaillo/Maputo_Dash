
# %%
import pickle
from dataclasses import dataclass, asdict
from maad.util import power2dB, format_features
from maad.sound import spectrogram, smooth, median_equalizer
from maad.rois import create_mask, select_rois
import numpy as np
from plotly import data
import soundfile as sf


@dataclass
class ROIDetector:
    fmin: int = 500
    fmax: int = 12000
    mode_bin = 'relative'
    param1: int = 10
    param2: int = 0.9
    display: bool = False
    dB_max: int = 96
    samplerate: int = 44100
    smooth: bool = True
    median_equalizer: bool = True

    def process_file(self, filen: str):
        data = {}
        audio_buffer, fs = sf.read(filen)
        self.tn, self.fn, self.ext, self.spectro = self.get_processed_spectro(
            audio_buffer, fs)
        return self.spectro, self.tn, self.fn, self.ext

    def get_roi_coordinates(self, Sxx_db_noNoise_smooth, ext, param1, param2):
        self.rois = self.get_df_rois(ext, self.spectro)
        return self.rois

    def get_df_rois(self, ext, Sxx_db_noNoise_smooth, tn, fn):

        im_mask = create_mask(im=Sxx_db_noNoise_smooth, mode_bin='relative',
                              bin_std=self.param1, bin_per=self.param2,
                              verbose=False, display=self.display)

        _, df_rois = select_rois(im_mask, min_roi=25, max_roi=None,
                                 display=self.display,
                                 **{'extent': ext, 'figsize': (4, 13)})

        self.rois = format_features(
            df_rois, tn, fn).to_dict("records")

        return self.rois

    def get_processed_spectro(self, audio_buffer, fs):
        max_Amp = np.abs(audio_buffer).max()
        Sxx_power, tn, fn, ext = spectrogram(
            audio_buffer/max_Amp, fs, flims=(self.fmin, self.fmax), display=False)
        Sxx_power_noNoise = median_equalizer(
            Sxx_power, display=False, **{'extent': ext})
        Sxx_db_noNoise = power2dB(Sxx_power_noNoise)
        Sxx_db_noNoise_smooth = smooth(Sxx_db_noNoise, std=0.5,
                                       display=False, savefig=None,
                                       **{'vmin': 0, 'vmax': self.dB_max, 'extent': ext})

        return tn, fn, ext, Sxx_db_noNoise_smooth

    def save_params(self):
        with open('test_pickle.pickle', 'wb') as handle:
            pickle.dump(data, handle)


# %%
