import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import json

style.use("fivethirtyeight")

report_max = int(input("How many reports shall be shown at max? "))
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    dict = {}
    path = "Documents\Python\data\data.json"
    with open (path, "r") as jsonfile:
        dict = json.loads(jsonfile.read())
    x = []
    y = []
    y2 = []
    y3 = []
    for i in list(reversed(list(dict)))[0:report_max]:
        x_value = int(i)
        y_value = float(dict[i][0])
        y2_value = float(dict[i][2])
        y3_value = float(dict[i][3])
        x.append(x_value)
        y.append(y_value)
        y2.append(y2_value)
        y3.append(y3_value)
    ax1.clear()
    ax1.plot(x, y2, color='blue', label='Mean')
    ax1.plot(x, y3, color='red', label='Variance')
    ax1.plot(x, y, color='black', label='Current Score')

    plt.title('Mood Monitor', fontsize=14)
    plt.xlabel('Report Nr.', fontsize=14)
    plt.ylabel('Value', fontsize=14)
    plt.legend()

    plt.gcf().autofmt_xdate(rotation = 90)

ani = animation.FuncAnimation(fig, animate, interval=4000)
plt.show()
