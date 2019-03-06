import pandas as pd
from flask import Flask, render_template, request
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pygal

d = pd.read_csv('https://biswanandastorage.blob.core.windows.net/biswacontainer/minnow.csv')
df_cls1 = pd.DataFrame(data=d)
df = df_cls1

e_d = pd.read_csv('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv')
e_df = pd.DataFrame(data=e_d)


print(df_cls1.columns)

application = app = Flask(__name__)

print(df_cls1.columns)

@app.route('/')
def hello_world():
    return render_template('quiz5.html')



# def plot(df, conditions, groupby=None, chartType=None, orientation='vertical', title='Graph'):

@app.route('/chart')
def plot():
    conditions = ((df.survived == 1) & (df.sex == 'female'))
    chartType = request.args.get('ChartType','bar', type=str)
    orientation = request.args.get('Orientation','vertical', type=str)
    title = request.args.get('Title','Graph',type=str)

    groupby = request.args.get('groupby','none',type=str)
    data_bar = df[conditions]
    lab = '-'.join(groupby)
    if groupby:
        data_bar = data_bar.groupby(groupby).size()
    data = dict(data_bar)
    labels = []
    values = []
    for k,v in data.items():
        labels.append(lab+str(k))
        values.append(v)
    if chartType == 'bar':
        plot_bar(labels,values,orientation,title)
    elif chartType == 'pie':
        plot_pie(labels,values,title)

    plt.savefig('./static/images/cluster.png')

    return render_template('image.html')

def plot_bar(labels, values,orientation,title):
    if orientation=='horizontal':
        my_colors = 'rgbkymc'
        fig, ax = plt.subplots()
        y_pos = np.arange(len(labels))
        ax.barh(y_pos, values)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_title(title)
    else:
        my_colors = 'rgbkymc'
        plt.bar(labels, values)
        plt.title(title)
        plt.xticks(labels, labels)

    plt.savefig('./static/images/cluster.png')

    return render_template('image.html')


def plot_pie(labels,values,title):
    plt.pie(values, labels=labels, autopct='%1.1f%%', shadow=True,color=(0.2, 0.4, 0.6, 0.7))
    plt.title(title)
    # plt.show()
    plt.savefig('./static/images/cluster.png')

    return render_template('image.html')

if __name__ == '__main__':
    app.run()