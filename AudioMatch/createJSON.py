import AudioAnalysis as AA
import os
import json
import numpy as np

path = "/Users/WLY/Desktop/Project/sound"

def getFiles(path):
    #get all the file,assume that all the audio file in the same
    filenames = []
    for files in os.walk(path):
        filenames = files[2]
    return filenames

def generateData():
    #generate features data and store them in json file
    files = getFiles(path)
    datas = []
    for file in files:
        print file
        filePath = path + "/" + file
        [param, data, time] = AA.waveRead(filePath)
        param = list(param)
        #generate features which used to compare
        th = AA.getThreshold(data[0])
        th = list(th)
        fregMF = AA.genFragMainFreq(data[0], param[3], AA.fregLen * 0.025)
        features = AA.getFeatures(data[0], param[2])
        zcr = features[0].tolist()
        energy = features[1].tolist()
        meanZcr = np.mean(features[0])
        stdZcr = np.std(features[0])
        meanE = np.mean(features[1])
        stdE = np.std(features[1])
        obj = {'name' : file, 'param' : param, 'threshold': th, 'fregMF' : fregMF,
               'zcr' : zcr, 'meanZCR' : meanZcr, 'stdZCR' : stdZcr,
               'Energy' : energy, 'meanE' : meanE, 'stdE' : stdE}
        datas.append(obj)
    with open('audioDatas.json', "w") as f:
        json.dump(datas, f)
    print "finished!"



def main():
    generateData()
    print "successfully create json file!"


if __name__ == "__main__":
    main()