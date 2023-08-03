import matplotlib.animation as animation
import matplotlib.pyplot as plt


def animate(i, file_name, fig, ax):
    """
    Function creating live updating graphs. Parameter "func" of the 
    animation.FuncAnimation class. the function is called at each frame.  

    Parameters:
        i - Each frame of the animation.
        file_name - Name of temporary file where sensor data are stored.
        fig - Figure, The top level container for all the plot elements.
        ax - An Axes object encapsulates all the elements of an individual subplot in a figure.

    """
    pullData = open(file_name, "r").read()
    dataList = pullData.split('\n')
    xList = []
    yList = []
    for eachLine in dataList:
        if len(eachLine) > 1:
            x, y = eachLine.split(',')
            xList.append(int(x))
            yList.append(int(y.strip()))
    ax[0, 0].clear()
    if len(xList) == 0:
        a[0, 0].set_ylim([-1, 1])
    else:
        a[0, 0].set_ylim([-1, max(yList[-400:])+1])
    if len(xList) >= 400:
        a[0, 0].plot(xList[-400:], yList[-400:])
    else:
        a[0, 0].plot(xList, yList)

    # TODO: extend plotting more charts, when more sensors will be connected
    # xList_0_0 = []
    # xList_0_1 = []
    # xList_1_0 = []
    # xList_1_1 = []
    # yList = []
