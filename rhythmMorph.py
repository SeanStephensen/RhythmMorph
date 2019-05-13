#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 15:50:09 2019

@author: seanstephensen
"""
#***************************************************************INPUTS
tempo = 100 #bpm
sub1 = 5 #subdivision 1
accents1 = [1,2,4,5] #which notes of subdivision 1 are accented
sub2 = 4 #subdivision 2
accents2 = [1,2,3,4]
morphFactor = 50 #morph percent (5% = pure rhythm 1, 100% = pure rhythm 2) NEED TO CHECK WHY low values break it

#************************************************************LIBRARIES
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

#************************************************************Constants
fs = 44100 #sample rate [Hz]
durs = [1e-3,2e-3,3e-3] #duration of a click [s] for [base rhythm, new rhythm, bpm pulse]
tones = [500,1000,2000,9000] #freqs of clicks [Hz]
volumes = [0,0.5,10] #Relative volume (0-1 scale) of tones for [base rhythm, new rhythm, bpm pulse]
loopLength = 4 #scale for how many times you want to loop (2^n)

#*********************************************************CALCULATIONS
def main():
    pattern1 = makeArray(sub1,accents1)
    pattern2 = makeArray(sub2,accents2)
    newPattern = morph(pattern1,pattern2,morphFactor)
    visualize(pattern1,pattern2,newPattern)
    getSound(pattern1,pattern2,newPattern)
    return

def domain(jj): #creates a time domain suitable for graphing
    yy = np.linspace(1,5,len(jj),endpoint=0)
    return yy

def getSound(beat1,beat2,beatNew):
    signals = [] #this list will hold all the signal arrays
    signals.append(makeWave(np.ones(1),tones[-1],volumes[-1],durs[2])) #quarter note bpm pulse added
    signals.append(makeWave(beat1,tones[0],volumes[0],durs[0])) #base rhythm 1 added
    signals.append(makeWave(beat2,tones[1],volumes[0],durs[0])) #base rhythm 2 added
    signals.append(makeWave(beatNew,tones[2],volumes[2],durs[1])) #new rhythm added
    play(signals)
    return

def makeArray(sub,acc): #creates an accented array
    try:
        arr = np.zeros(sub) #makes an array of sub values (e.g. 5 long for quintuplets)
        acc = np.array(acc)-1 #translates acc to an array for subscripting
        arr[acc] = 1 #places an accent on prescribed values
    except:
        print("Too many accents or accents out of subdivision range!")
    return arr

def makeWave(rhythm,pitch,vol,size):
    time = 60/tempo #time for 1 quarter note [s]
    nLong = int(size*fs) #number of samples for a click length
    pattern = np.empty(0) #empty waveform pattern made
    add = int((1/len(rhythm))*(time*fs - nLong*len(rhythm))) #how much space added after each click
    for ii in range(len(rhythm)): #waveform built
        pattern = np.append(pattern,rhythm[ii]*np.ones(nLong))
        pattern = np.append(pattern,np.zeros(add))
    mask = pattern*vol #pattern mask with volume adjustment
    waveform = (np.sin(2*np.pi*np.arange(time*fs)*pitch/fs)) #waveform generated
    #shitty temporary fix part 1: FIX THE INT PROBLEM
    if len(mask)<len(waveform):
        waveform = waveform[0:len(mask)]
    elif len(mask)>len(waveform):
        mask = mask[0:len(waveform)]
    else:
        pass
    #END SHITTY FIX
    waveform = mask*waveform.astype(np.float32) #final mask, final conversion
    return waveform

def morph(arr1,arr2,factor): #morphs to a weighted average array
    try:
        fac = int(factor)/100 #morph % converted to decimal
        req = 100 #arbitrary over ride because equation below is giving inaccuracies
        #req = int(len(arr1)*len(arr2)/fac) #how many subdivisions are required for new rhythm?
        #true values from first array converted to "percentages along the array":
        vals1 = (np.nonzero(arr1)[0])/len(arr1)
        vals2 = (np.nonzero(arr2)[0])/len(arr2)
        #this (weighted) averages the "time percentages" of the two arrays:
        newIndices = req*(vals1+(vals2-vals1)*fac)
        #newIndices = req*(fac*vals1 + (1-fac)*vals2) another option for weighted average
        #these 2 weighted average equations give different results sometimes due to rounding errors
        newIndices = np.around(newIndices).astype(int)
        newArr = np.zeros(req) #'average' array created
        newArr[newIndices] = 1 #'average' accents created
    except:
        print("Unequal number of accents!")
    return newArr

def play(waves):
    #SHITTY FIX PART 2:
    lengths = [len(pp) for pp in waves]
    wavesNew = []
    for item in waves:
        if len(item) > min(lengths):
            item = item[0:min(lengths)]
            wavesNew.append(item)
        else:
            wavesNew.append(item)
    #END SHITTY FIX
    master = sum(wavesNew) #adds individual signals
    for ii in range(loopLength): #range argument controls length of looping
        master = np.append(master,master) #Shitty form of looping for now
    sd.play(master,fs) #produces sound
    return

def visualize(v1,v2,v3):
    ticks = [1,2,3,4]
    yLine = [1,2]
    plt.figure()
    plt.scatter(domain(v1),v1,[120]*v1,'b')
    plt.scatter(domain(v2),2*v2,[120]*v2,'r')
    plt.scatter(domain(v3),(1+morphFactor/100)*v3,[120]*v3,'g')
    for item in ticks:
        plt.axvline(x=item,ls='dashed',c='k')
    for kk in list(range(int(sum(v1)))):
        x1 = domain(v1)[np.nonzero(v1)[0][kk]]
        x2 = domain(v2)[np.nonzero(v2)[0][kk]]
        plt.plot([x1,x2],yLine,'y-')
    plt.ylim(0.75,2.25)
    plt.xlim(0.9,5)
    plt.xticks(ticks)
    plt.yticks([1,(1+morphFactor/100),2],['Base Rhythm 1','New Rhythm','Base Rhythm 2'])
    plt.show
    return

main()