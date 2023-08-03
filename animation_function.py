import matplotlib.animation as animation
import matplotlib.pyplot as plt


def animate(i, file_name, f, a):
    pullData = open(file_name, "r").read()
    dataList = pullData.split('\n')
    xList = []
    yList = []
    for eachLine in dataList:
        if len(eachLine) > 1:
            x, y = eachLine.split(',')
            xList.append(int(x))
            yList.append(int(y.strip()))
    a[0,0].clear()
    if len(xList) == 0:
        a[0,0].set_ylim([-1, 1])
    else:
        a[0,0].set_ylim([-1, max(yList[-400:])+1])
    if len(xList) >= 400:
        a[0,0].plot(xList[-400:], yList[-400:])
    else:
        a[0,0].plot(xList, yList)

    ############ future ############
    pullData = open(file_name, "r").read()
    dataList = pullData.split('\n')
    xList_1 = []
    xList_2 = []
    xList_3 = []
    xList_4 = []
    yList = []
    
