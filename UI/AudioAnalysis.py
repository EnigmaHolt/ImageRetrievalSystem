from pyAudioAnalysis import audioFeatureExtraction
from scipy.fftpack import fft
import numpy as np
import wave
import json

fregLen = 220000
stdEW = 1.0
stdZCRW = 1.0
meanEW = 0.5
meanZCRW = 0.5
thW = 0.001
mfW = 0.1

class compObj:
    name = ""
    diff = 0

    def prt(self):
        print "name = ", self.name
        print "diff = ", self.diff



def waveRead(path):
    wavefile = wave.open(path, "rb")
    params = wavefile.getparams()
    framerate = params[2]
    framenum = params[3]
    wavedata = wavefile.readframes(framenum)
    wavefile.close()
    dataUse = np.fromstring(wavedata, dtype=np.short)
    dataUse.shape = -1,2
    dataUse = dataUse.T
    time = np.arange(0, framenum) * (1.0 / framerate)
    return params, dataUse, time


def getThreshold(data):
    #return the threshold of whole audio
    minV = np.min(data)
    maxV = np.max(data)
    minV = int(minV)
    maxV = int(maxV)
    return minV,maxV

def getMainFreq(data):
    #return the main frequency of whole audio
    data = data[0:fregLen]
    fdata = abs(fft(data))
    f = fdata.tolist()
    print len(f)
    mf = f.index(max(f))
    return mf

def getFeatures(data, framrate):
    #0:short time crt
    #1:short time energy
    #2:short time energy entropy
    F = audioFeatureExtraction.stFeatureExtraction(data, framrate, 0.050 * framrate, 0.025 * framrate)
    #print F.shape
    features = []
    features.append(F[0])
    features.append(F[1])
    features.append(F[2])
    return features

def genFragMainFreq(data, frameNum, step):
    mainFreqs = []
    start = 0
    while start + fregLen - 1 < frameNum:
        tempD = data[start : start + fregLen]
        fd = abs(fft(tempD))
        fd = fd.tolist()
        mf = fd.index(max(fd))
        mainFreqs.append(mf)
        start += step
    return mainFreqs


def findMostApproachFreqDiff(freqQ, DBfreq):
    #freqQ is the query main freq, and DBfreq is the fregment Main Frequency
    #return the most approaching frequency value
    min = freqQ
    mf = freqQ
    for f in DBfreq:
        diff = abs(freqQ - f)
        if diff < min:
            min = diff
            mf = f
    return min

def calParams(path):
    [params, data, time] = waveRead(path)
    mF = getMainFreq(data[0])
    th = getThreshold(data[0])
    features = getFeatures(data[0],params[2])
    meanZRC = np.mean(features[0])
    stdZRC = np.std(features[0])
    meanE = np.mean(features[1])
    stdE = np.std(features[1])
    return[mF, th, meanZRC, stdZRC, meanE, stdE]

def sortAndgeneCoeff(diff):
    diff.sort(cmp=None, key=lambda x:x.diff, reverse=False)
    print len(diff)
    idx = len(diff)-1
    max = diff[idx].diff
    for d in diff:
        d.diff = (max - d.diff)/max

#calculate diffenrent with the video in databases
def compareSimilarity(queryPath):
    #load DBdatas from json file
    qData = calParams(queryPath)
    with open('audioDatas.json',"r") as f:
        DBdatas = json.load(f)
    #compare the similarity
    print "compare soon!"
    different = []
    for obj in DBdatas:
        cur = compObj()
        cur.name = obj['name']
        curTh = obj['threshold']
        thDiff = np.mean(abs(curTh[0] - qData[1][0])+abs(curTh[1] - qData[1][1]))
        meanZDiff = abs(obj['meanZCR'] - qData[2])
        meanEDiff = abs(obj['meanE'] - qData[4])
        stdZDiff = abs(obj['stdZCR'] - qData[3])
        stdEDiff = abs(obj['stdZCR'] - qData[5])
        freqDiff = findMostApproachFreqDiff(qData[0], obj['fregMF'])
        totalD = thW*thDiff + meanEDiff*meanEW + meanZDiff*meanZCRW + stdEDiff*stdEW + stdZDiff*stdZCRW + mfW * freqDiff
        cur.diff = totalD
        different.append(cur)
    #different.sort(cmp=None, key=lambda x:x.diff, reverse=False)
    sortAndgeneCoeff(different)
    return different


if __name__ == "__main__":
    #used to test
    diff = compareSimilarity("/Users/haowu/Documents/576/project/query/first/first.wav")

    f = open('/Users/haowu/Documents/576/project/test.txt', 'w')

    for d in diff:
        f.write(d.name+ " : "+str(d.diff))
    f.close()