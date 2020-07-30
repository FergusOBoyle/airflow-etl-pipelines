


def extract_traffic_data():

    import os
    import time
    from datetime import datetime, timedelta
    from sys import platform

    import csv
    import codecs
    import requests
    import yaml
    import pyodbc 

    from aws_functions import get_secret


    #obtain DB credentials from the AWS secrets manager
    secret = eval(get_secret())

    #extract the name of the directory that this file is located in, regardless of the current working directory.
    script_dir = os.path.dirname(__file__)


    if platform == "linux": 
        driver= "{/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.5.so.2.1}"
    elif platform == "win32":
        driver= "{SQL Server}"
    server = "traffic-db-sqlserver.c0s0xrpsinuo.eu-west-1.rds.amazonaws.com"
    database = "traffic"
    user = secret["username"]
    password = secret["password"]

    conn = pyodbc.connect("Driver=" + driver + ";"
                        "Server=" + server + ";"
                        "Database=" + database + ";"
                        "uid=" + user + ";"
                        "pwd=" + password + ";")


    yesterday_format1 = datetime.strftime(datetime.now() - timedelta(1), '%Y/%m/%d')
    yesterday_format2  = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')

    download_day_format1 = yesterday_format1
    download_day_format2 = yesterday_format2
    print("Download day:" , download_day_format1)

    x = "https://data.tii.ie/Datasets/TrafficCountData/" + download_day_format1 + "/per-site-class-aggr-" + download_day_format2 + ".csv"

    print(x)

    response = requests.get("https://data.tii.ie/Datasets/TrafficCountData/" + download_day_format1 + "/per-site-class-aggr-" + download_day_format2 + ".csv")

    #https://stackoverflow.com/questions/30483977/python-get-yesterdays-date-as-a-string-in-yyyy-mm-dd-format/30484112

    #raw_data = response.text
    text = codecs.iterdecode(response.iter_lines(), 'utf-8') #response.iter_lines()
    reader = csv.reader(text, delimiter=',')


    cursor_desc = conn.cursor()
    #cursor_desc.execute('SELECT * FROM traffic_daily_aggregates')


    next(reader) #skip first row
    params = [(row) for row in reader]
    #params = [(row) for i, row in enumerate(reader) if i < 100]



    cursor_desc.fast_executemany = True
    sql = "INSERT INTO traffic_daily_aggregates  VALUES (?, ?, ?, ?, ?, ?)"
    t0 = time.time()
    cursor_desc.executemany(sql, params)
    conn.commit()
    print(f'{time.time() - t0:.1f} seconds')