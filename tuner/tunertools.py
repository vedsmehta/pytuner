"""Helper Functions for tuner.py"""

from itertools import groupby
import bisect
import numpy as np
from scipy.io.wavfile import read as wavread
from scipy.signal import hamming
import sounddevice as sd
import amfm_decompy.basic_tools as basic
import amfm_decompy.pYAAPT as pYAAPT


__author__ = 'Vedant Mehta'

def audio_read(wav):
    """
    reads .wav and returns numpy.ndarray

    Parameters:
    -----------
        wav str:
            path to wav file
    """
    [sr, sig] = wavread(wav)
    return sr, sig

def play(audio_path):
    """
    play audio as numpy.ndarray

    Parameters:
    --------------
    audio_path str:
        path to audio file

    """
    sd.play(audio_read(audio_path)[1], samplerate=44100, device="Speakers")

# implementing YIN algorithm
# (http://recherche.ircam.fr/equipes/pcm/cheveign/ps/2002_JASA_YIN_proof.pdf)
#  - Autocorrelation and YIN


def cummalative_mean_norm_df(df, N):
    """
    takes the cummalative mean for normalized difference function

    Parameters:
    -----------------
    df iterable:
        difference function
    N int:
        length of difference function
    """

    # cummalative mean normalized difference function derived from
    # equation 8 of YIN paper
    CMNDF = df[1:] * list(range(1, N)) / np.cumsum(df[1:]).astype(float)
    return np.insert(CMNDF, 0, 1)


def differenceFunction(audio, w, t_max):
    """
    function to calculate the difference of an unknown window 
``    (between two different numbers unknown)

    Args:
    -----------------
    audio iterable:
        audio passed through audio_read()
    w int:
        length of audio
    t_max int:
        maximum time constant

    """

    x = np.array(audio, np.float64)
    w = x.size
    t_max = min(t_max, w)
    x_cumsum = np.concatenate((np.array([0.]), (x * x).cumsum()))
    size = w + t_max
    p2 = (size // 32).bit_length()
    nice_numbers = (16, 18, 20, 24, 25, 27, 30, 32)
    size_pad = min(x * 2 ** p2 for x in nice_numbers if x * 2 ** p2 >= size)
    fc = np.fft.rfft(x, size_pad)
    conv = np.fft.irfft(fc * fc.conjugate())[:t_max]
    df = x_cumsum[w:w - t_max:-1] + x_cumsum[w] - x_cumsum[:t_max] - 2 * conv
    return df


def pitch(CMNDF, t_min, t_max, ht=0.1):
    """
    find pitch of certain time interval
    Args:
    ----------------
    CMNDF iterable:
        cummalative mean normalized difference function
    t_min :
        minumum time constant
    t_max (undefined):
        maximum time constant
    ht=0.1 float:
            harmonic threshold

    """

    t = t_min
    while t < t_max:
        if CMNDF[t] < ht:
            while t + 1 < t_max and CMNDF[t + 1] < CMNDF[t]:
                t += 1
            return t
        t += 1

    return 0    # if unvoiced


def YIN(sig, sr, wl=882, ws=441, f0_min=50,
        f0_max=500, ht=0.1):
    """

    Implement the YIN algorithm. Notice how 
    differenceFunction, cummalative_mean_norm_df, and pitch
    are all helper functions for this tool.

    Parameters:
    --------------
    sig iterable:
        numpy array of audio
    sr int:
        samplerate
    wl=882 int:
        length of calculation window for pitch
    ws=441 int:
        step for calculation window
    f0_min=50 int:
        minimum frequency threshold
    f0_max=500 int:
        maximum frequency threshold
    ht=0.1 float:
        harmonic threshold

    """

    t_min = int(sr / f0_max)
    t_max = int(sr / f0_min)

    timeScale = range(0, len(sig) - wl, ws)
    times = [t/float(sr) for t in timeScale]
    frames = [sig[t:t + wl] for t in timeScale]

    pitches = [0.0] * len(timeScale)
    harmonic_rates = [0.0] * len(timeScale)
    argmins = [0.0] * len(timeScale)

    for i, frame in enumerate(frames):

        # Compute YIN
        df = differenceFunction(frame, wl, t_max)
        CMNDF = cummalative_mean_norm_df(df, wl)
        p = pitch(CMNDF, t_min, t_max, ht)

        # Get results
        if np.argmin(CMNDF) > t_min:
            argmins[i] = float(sr / np.argmin(CMNDF))
        if p != 0:  # A pitch was found
            pitches[i] = float(sr / p)
            harmonic_rates[i] = CMNDF[p]
        else:
            harmonic_rates[i] = min(CMNDF)

    return pitches, harmonic_rates, argmins, times



def yaapt(x, fs=44100, f0_min=40, f0_max=500):
    """ 

    "Yet another algorithm for pitch detection."
    This is a python implementation of YAAPT which uses AMFM decompy.


    Parameters
    ----------
    x : iterable
        signal or sound data
    fs : int
        samplerate of x
    f0_min : real
        minimum fundamental frequency
    f0_max : int
        maximum fundamental frequency estimate
    """
    signal = basic.SignalObj(data=np.array(x), fs=fs)
    return pYAAPT.yaapt(signal, f0_min=f0_min, f0_max=f0_max) 
        

def notes():
    """ returns list of playable notes on guitar """
    notes_list = [['E2', '82.41'],
                  ['F2', '87.31'],
                  ['F#2/Gb2', '92.5'],
                  ['G2', '98'],
                  ['G#2/Ab2', '103.83'],
                  ['A2', '110'],
                  ['A#2/Bb2', '116.54'],
                  ['B2', '123.47'],
                  ['C3', '130.81'],
                  ['C#3/Db3', '138.59'],
                  ['D3', '146.83'],
                  ['D#3/Eb3', '155.56'],
                  ['E3', '164.81'],
                  ['F3', '174.61'],
                  ['F#3/Gb3', '185'],
                  ['G3', '196'],
                  ['G#3/Ab3', '207.65'],
                  ['A3', '220'],
                  ['A#3/Bb3', '233.08'],
                  ['B3', '246.94'],
                  ['C4', '261.63'],
                  ['C#4/Db4', '277.18'],
                  ['D4', '293.66'],
                  ['D#4/Eb4', '311.13'],
                  ['E4', '329.63'],
                  ['F4', '349.23'],
                  ['F#4/Gb4', '369.99'],
                  ['G4', '392'],
                  ['G#4/Ab4', '415.3'],
                  ['A4', '440'],
                  ['A#4/Bb4', '466.16'],
                  ['B4', '493.88'],
                  ['C5', '523.25'],
                  ['C#5/Db5', '554.37'],
                  ['D5', '587.33'],
                  ['D#5/Eb5', '622.25'],
                  ['E5', '659.25']]
    for i in range(len(notes_list)):
        notes_list[i][1] = float(notes_list[i][1])
    return notes_list


def mean(arr):
    """
    calculate mean of an array

    Parameters:
    --------------
    arr iterable:
        array to be averaged

    """
    
    return sum(arr)/len(arr)


def avg_pitch(input_list: list):
    """
    Takes the largest consecutive nonzero substring and averages it.

    Parameters:
    --------------
    input_list : list
        array or list to be manipulated/averaged.


    """

    g = groupby(input_list, key=lambda x: x > 0.0)
    m = max([list(s) for v, s in g if v > 0.0], key=len)
    return mean(m)


def quantize(num, quant):
    """
    round to the nearest value in a list
    Parameters:
    --------------
    num float:
        number to be quantized
    quant iterable:
        list to be quantized to

    """
    
    mids = [(quant[i] + quant[i + 1]) / 2.0
            for i in range(len(quant) - 1)]
    ind = bisect.bisect_right(mids, num)
    return quant[ind]

