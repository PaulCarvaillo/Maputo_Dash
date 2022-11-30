# %%
# Import math, plotting and sound libraries
import numpy as np
import matplotlib.pyplot as plt
from soundsig.sound import BioSound
from soundsig.sound import WavFile
import soundfile as sf
import librosa
import os


def create_h5_objects_from_dir(path='/Users/Paul/Paul/Desktop/My_projects/Bioacoustics/BioSoundTutorial-master/datasets/xenocanto/'):

    # Go to the folder that has the wav files
    os.chdir(path)
    sounds_root_path = path+'/wav'
    # This will be the output directory
    if not os.path.exists('h5files'):
        os.makedirs('h5files')

    for root, dirs, files in os.walk(sounds_root_path):
        dirname = root.split(os.path.sep)[-1]

        for file in files:
            if file.endswith('.wav'):
                filepath = os.path.join(str(root), str(file))
                outputname = dirname + '_' + str(file)

                # workaround RIFF ID Bug on WavFile:
                temp, sr = librosa.load(filepath)

                sf.write('tmp.wav', temp, sr)
                path, extension = os.path.splitext(filepath)
                birdname = path.rsplit(sep='/')[-2]
                soundId = path.rsplit(sep='/')[-1]
                outputfilename = birdname+'_'+soundId+extension
                soundIn = WavFile('tmp.wav')
                # normalize
                maxAmp = np.abs(soundIn.data).max()
                # makeBiosound object
                calltype = 'calls'
                myBioSound = BioSound(soundWave=soundIn.data.astype(
                    float)/maxAmp, fs=float(soundIn.sample_rate), emitter=birdname, calltype=calltype)

                # insert data to compute here:
                myBioSound.spectroCalc(spec_sample_rate=1000,
                                       freq_spacing=50, min_freq=0, max_freq=10000)
                myBioSound.spectrum(f_high=10000)

            # Save the results
                fh5name = 'h5files/%s.h5' % (birdname+'_'+soundId)
                myBioSound.saveh5(fh5name)
