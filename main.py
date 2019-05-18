import re
import math
import numpy as np
import matplotlib.pyplot as plt

sdkData = []


def getdata():
    if len(sdkData) == 0:
        with open('./testcase/sdkInfo') as fileData:
            info = []
            data = fileData.read().splitlines()
            for line in data:
                linedata = line.strip().split()
                if re.match(r'\d{13}.*', linedata[0]) and linedata[1] != 'TYPE_WIFI':
                    info.append(linedata)
            for i in range(0, len(info), 4):
                b = info[i: i+4]
                datadict = {}
                for item in b:
                    datadict['time'] = item[0]
                    datadict[item[1]] = item[2: 5]
                sdkData.append(datadict)
    return sdkData


def callistsumbyindex(start, end, array):
    sum = 0
    index = start
    while start <= index <= end:
        sum += array[index]
        index += 1
    return sum


def smoothacc(accs, width=19):
    length = len(accs) - 1
    halfW = width / 2
    targets = []
    for index, item in enumerate(accs):
        acc = 0
        if index < halfW:
            end = index * 2 + 1
            acc = callistsumbyindex(0, end, accs) / (end + 1)
        elif index < length - halfW:
            acc = callistsumbyindex(index - halfW, index + halfW, accs) / width
        elif index < length:
            acc = callistsumbyindex(index * 2 - length, length, accs) / (2 * (length - index) + 1)
        else:
            acc = item
        targets.append(acc)
    return targets


def findpace(list, times):
    minpeak = 10.5
    minvalley = 8.8
    timewindow = 0.2
    lastpeak = {
        'time': 0,
        'acc': 0,
            }
    lastvalley = {
        'time': 0,
        'acc': 0,
            }
    pace = []
    for index, item in enumerate(list):
        time = int(times[index])
        left = 0
        right = 0
        if 0 < index < len(list) - 1:
            left = list[index - 1]
            right = list[index + 1]
        if item > minpeak \
                and time - lastpeak['time'] > timewindow\
                and left < item < right:
            pace.append(item)
            lastpeak['time'] = time
            lastpeak['acc'] = item
        elif item < minvalley \
                and time - lastvalley['time'] > timewindow\
                and left > item > right:
            pace.append(item)
            lastvalley['time'] = time
            lastvalley['acc'] = item
    stepLens = []
    i = 0
    a = 0.8
    b = 0.2
    while i < len(pace) - 1:
        peak = max(pace[i], pace[i + 1])
        vallley = min(pace[i], pace[i + 1])
        pv = peak - vallley
        step = a * pow(pv, 1 / 4) + b * math.log(pv, math.e)
        stepLens.append(step)
        i += 2
    return stepLens


def handlegyros(gyroscopes, times):
    gyroeds = []
    time = 0
    for index, item in enumerate(gyroscopes):
        [wx, wy, wz] = item
        timecurrent = int(times[index])
        ww = pow((pow(float(wx), 2) + pow(float(wy), 2) + pow(float(wz), 2)), 0.5) * (timecurrent - time)
        time = timecurrent
        sinW = math.sin(ww / 2) / ww
        [q0, q1, q2, q3] = [math.cos(ww / 2), wx * sinW, wy * sinW, wz * sinW]
        RM = np.array([
            [1 - 2 * (q2 * q2 + q3 * q3), 2 * (q1 * q2 - q0 * q3), 2 * (q1 * q2 + q0 * q3)],
            [2 * (q1 * q2 + q0 * q3), 1 - 2 * (q1 * q1 + q3 * q3), 2 * (q2 * q3 - q0 * q1)],
            [2 * (q1 * q3 - q0 * q2), 2 * (q2 * q3 + q0 * q1), 1 - 2 * (q1 * q1 + q2 * q2)]])
        gyroeds.append(RM)
    return gyroeds


def main():
    datas = getdata()
    accList = []
    timelist = []
    gyroscopes = []
    for item in datas:
        accs = item.get('TYPE_ACCELEROMETER')
        acced = 0
        for acc in accs:
            acced += pow(float(acc), 2)
        acced = pow(acced, 0.5)
        timelist.append(item.get('time'))
#        gyroscopes.append(item.get('TYPE_GYROSCOPE'), item.get('time'))
        accList.append(acced)
    # find peak valley
    accssmoothed = smoothacc(accList)
    paces = findpace(accssmoothed, timelist)
    plt.plot(paces, label='pace')
    plt.legend()
    plt.show()

main()

