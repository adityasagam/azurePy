# from flask import Flask
from flask import Flask, request, render_template, make_response
import pyodbc
import time
import redis
import _pickle as pickle
import random
import csv
import json
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
rds = redis.StrictRedis(host='AzurePyRed.redis.cache.windows.net', port=6380, db=0, password='fkHefGi1Nlzj6nUkYoQYZI24wvOrlPMveiw95rHLn1U=', ssl=True)

@app.route('/')
def my_form():
    return render_template('my-form.html')

@app.route('/barchart')
def getStateYearPop():
    cnxn = getDBCnxn()
    cursor = cnxn.cursor()
    cursor.execute("select [state], [2010] from population")
    rows = cursor.fetchall()

    '''
    # Convert pyodbc row to list
    data = []
    for row in rows:
        data.append([x for x in row])
    '''
    cursor.close()
    cnxn.close()

    x_labels = ()
    y_axis = []
    for i, row in enumerate(rows):
        #print(rows[i][1])
        x_labels = x_labels + (row.state,)
        y_axis.append(rows[i][1])
    #print(y_axis)



    #objects = ('Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
    y_pos = np.arange(len(x_labels))
    #performance = [10, 8, 6, 4, 2, 1]
    performance = y_axis

    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, x_labels)
    plt.ylabel('Population')
    plt.title('Programming language usage')
    plt.show()

    return render_template('visuals.html', data=[])

@app.route('/piechart')
def getStateALlYearsPop():
    cnxn = getDBCnxn()
    cursor = cnxn.cursor()
    cursor.execute("select [state], [2010], [2011], [2012], [2013], [2014], \
                    [2015], [2016], [2017], [2018] from population where state=\'Alabama\'")
    rows = cursor.fetchall()

    '''
    # Convert pyodbc row to list
    data = []
    for row in rows:
        data.append([x for x in row])
    '''
    cursor.close()
    cnxn.close()

    y_axis = []
    for i in range(1, 10):
        #print(rows[i][1])
        y_axis.append(rows[0][i])
        print(y_axis)
    #print(y_axis)

    # Data to plot
    labels = '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018'
    sizes = y_axis
    #colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    #explode = (0.1, 0, 0, 0)  # explode 1st slice

    # Plot
    plt.pie(sizes, labels=labels,
            autopct='%1.1f%%', shadow=True, startangle=140)

    plt.axis('equal')

    #plt.show()
    img3 = BytesIO()
    plt.savefig(img3, format='png')

    img3.seek(0)
    plot_url = base64.b64encode(img3.getvalue())
    response = make_response(img3.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response
    #return render_template('visuals.html', data=[])


'''
@app.route('/getStateYearPopulation')
def getStateYearPopulation():

    code = request.args.get('code', '')
    year = request.args.get('year', '')

    cnxn = getDBCnxn()
    cursor = cnxn.cursor()

    sql = "SELECT population.state, population.["+year+"] FROM population, statecode\
           where statecode.code = \'"+ code +"\' and population.state = statecode.state"
    cursor.execute(sql)

    results = cursor.fetchall()
    cursor.close()
    cnxn.close()

    return render_template('7.html',year=year, state=code, result=results[0][1])
'''

'''
@app.route('/populationRange')
def getPopulationRange():
    cacheName = 'popRange'
    k = int(request.args.get('iterations', ''))

    if rds.exists(cacheName):
        isCache = 'with Cache'

        start_time = time.time()
        for i in range(0,k):
            results = pickle.loads(rds.get(cacheName))
        end_time = time.time()

        rds.delete(cacheName)
    else:
        isCache = 'without Cache'
        start_time = time.time()
        pop1 = request.args.get('pop1', '')
        pop2 = request.args.get('pop2', '')
        year = request.args.get('year', '')

        cnxn = getDBCnxn()
        cursor = cnxn.cursor()
        for i in range(0, k):
            sql = "SELECT state FROM population\
                   where "+year+" > "+ pop1+" and "+ year +" < "+ pop2
            cursor.execute(sql)
            results = cursor.fetchall()
        end_time = time.time()
        cursor.close()
        cnxn.close()
        rds.set(cacheName, pickle.dumps(results))

    return render_template('9.html',data=results, isCache=isCache, time=(end_time-start_time))
'''

'''
@app.route('/countCounty')
def getCountCounty():
    code = request.args.get('code', '')

    cnxn = getDBCnxn()
    cursor = cnxn.cursor()

    sql = "SELECT county.state, COUNT(county.county) FROM county, statecode\
           where statecode.code = \'"+code+"\' and county.state = statecode.state GROUP BY county.state"
    cursor.execute(sql)

    results = cursor.fetchall()
    cursor.close()
    cnxn.close()

    return render_template('8.html', state=code, result=results[0][1])
'''

'''
@app.route('/uploadPopulation')
def uploadPopulationData():
    sql_conn = getDBCnxn()
    cursor = sql_conn.cursor()

    start_time = time.time()

    cursor.execute('CREATE TABLE [dbo].[population](\
	[State] [nvarchar](50) NOT NULL,\
	[2010] [numeric](18, 0) NOT NULL,\
	[2011] [numeric](18, 0) NOT NULL,\
	[2012] [numeric](18, 0) NOT NULL,\
	[2013] [numeric](18, 0) NOT NULL,\
	[2014] [numeric](18, 0) NOT NULL,\
	[2015] [numeric](18, 0) NOT NULL,\
	[2016] [numeric](18, 0) NOT NULL,\
	[2017] [numeric](18, 0) NOT NULL,\
	[2018] [numeric](18, 0) NOT NULL)')

    with open('population.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            SQLCommand = ("INSERT INTO population "
                          "([State],[2010],[2011],[2012],[2013],[2014],[2015],[2016],[2017],[2018])"
                          "VALUES (?,?,?,?,?,?,?,?,?,?)")
            Values = [row['State'], int(row['2010'].replace(',','')), int(row['2011'].replace(',','')),
                      int(row['2012'].replace(',','')), int(row['2013'].replace(',','')),
                      int(row['2014'].replace(',','')), int(row['2015'].replace(',','')), int(row['2016'].replace(',','')),
                      int(row['2017'].replace(',','')), int(row['2018'].replace(',',''))]
            cursor.execute(SQLCommand, Values)
            cursor.commit()
            line_count = line_count + 1
            print("updated record number {}".format(line_count))
    end_time = time.time()

    return 'Data uploaded completely with time : ' + str(end_time - start_time)
'''

'''
@app.route('/fetchAll')
def fetchData():
    cacheName = 'testQueryRes'

    if rds.exists(cacheName):
        isCache = 'with Cache'

        start_time = time.time()
        results = pickle.loads(rds.get(cacheName))
        end_time = time.time()

        rds.delete(cacheName)
    else:
        isCache = 'without Cache'

        cnxn = getDBCnxn()
        cursor = cnxn.cursor()
        start_time = time.time()
        cursor.execute("select * from Earthquake")

        'Driver={ODBC Driver 13 for SQL Server};Server=tcp:mysqlpyserver.database.windows.net,1433;Database=myAzurePyDB; \
        Uid=azureuser@mysqlpyserver;Pwd={your_password_here};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'


        results = cursor.fetchall()
        end_time = time.time()

        cursor.close()
        cnxn.close()
        rds.set(cacheName, pickle.dumps(results))

    return render_template('results.html', data=results, time=(end_time - start_time), isCache=isCache)
'''

'''
rdsKeys = []


@app.route('/makeMultipleQueries')
def fetchMagQueries():
    cnxn = getDBCnxn()
    cursor = cnxn.cursor()

    if len(rdsKeys) > 0:
        isCache = 'with Cache'

        results = []
        start_time = time.time()
        for key in rdsKeys:
            results.extend(pickle.loads(rds.get(str(key))))
        end_time = time.time()

        #clean up
        for key in rdsKeys:
            rds.delete(key)
        del rdsKeys[:]
    else:
        isCache = 'without Cache'

        mag1 = float(request.args.get('mag1', ''))
        mag2 = float(request.args.get('mag2', ''))
        count = int(request.args.get('count', ''))

        start_time = time.time()

        results = []
        #totalRecords = 0
        for i in range(0, count):
            randomNum = str(round(random.uniform(mag1, mag2), 1))

            cursor.execute("select * from Earthquake where mag="+randomNum)
            currentRes = cursor.fetchall()
            print('Mag:', randomNum, 'Records:', len(currentRes))

            results.extend(currentRes)

            #totalRecords = totalRecords + len(currentRes)
            #print('totalRecords', totalRecords)

            #put current result into cache
            rds.set(randomNum, pickle.dumps(currentRes))
            rdsKeys.append(randomNum)

    print('keys ahe', rdsKeys)
    end_time = time.time()
    cursor.close()
    cnxn.close()
    return render_template('results.html', data=results, time=(end_time - start_time), isCache=isCache)
'''


def getDBCnxn():
    server = 'mysqlpyserver.database.windows.net'
    database = 'myAzurePyDB'
    username = 'azureuser'
    password = 'Azure123456'
    driver = '{ODBC Driver 17 for SQL Server}'
    return pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

'''
@app.route('/uploadData')
def my_form_post():
    import pandas as pd
    import sqlalchemy
    from pandas import DataFrame, read_csv

    file = r'all_month.csv'
    df = pd.read_csv(file)

    sql_conn = getDBCnxn()
    cursor = sql_conn.cursor()

    with open('all_month.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            SQLCommand = ("INSERT INTO Earthquake "
                          "(time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,magError,magNst,status,locationSource,magSource) "
                          "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
            Values = [row['time'], row['latitude'], row['longitude'], row['depth'],
                      row['mag'], row['magType'], row['nst'], row['gap'], row['dmin'], row['rms'],
                      row['net'], row['id'], row['updated'], row['place'], row['type'], row['horizontalError'],
                      row['depthError'], row['magError'], row['magNst'], row['status'], row['locationSource'], row['magSource']]
            cursor.execute(SQLCommand, Values)
            cursor.commit()
            line_count = line_count + 1
            print("updated record number {}".format(line_count))

    
    sql_conn.commit()
    cursor.close()
    sql_conn.close()
    return "Completed Upload!"
'''

'''
@app.route('/', methods=['POST'])
def my_form_post():
  text = request.form['text']
  processed_text = text.upper()
  return processed_text
def hello_world():
return 'Hello, World!\n This looks just amazing within 5 minutes'
'''

if __name__ == '__main__':
  app.run()