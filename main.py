import re
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


# def findpace(list, times, width):
#     length = len(list)
#     index = 0
#     preValley = list[0]
#     while index + width < length:
#         accstemp = list[index: index + width]
#         pos = 0
#         tempeak = accstemp[index]
#         for dex, item in enumerate(accstemp):
#             if item > tempeak:
#                 tempeak = item
#                 pos = dex
#
#         index += width


def main():
    datas = getdata()
    accList = []
    timelist = []
    accx = []
    accy = []
    accz = []
    for item in datas:
        accs = item.get('TYPE_ACCELEROMETER')
        acced = 0
        for acc in accs:
            acced += pow(float(acc), 2)
        acced = pow(acced, 0.5)
        timelist.append(item.get('time'))
        accList.append(acced)
        accx.append(float(accs[0]))
        accy.append(float(accs[1]))
        accz.append(float(accs[2]))
    # find peak valley
    # accssmoothed = smoothacc(accList)
    plt.plot(accx, label='x')
    plt.plot(accy, label='y')
    plt.plot(accz, label='z')
    plt.plot(accList, label='totally')
    plt.legend()
    plt.savefig("compare.png")
    plt.show()
main()

