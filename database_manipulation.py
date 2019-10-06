import sqlite3
from settings import *


def update_flag(conn, flagName, value):
    sql = ''' UPDATE flags
              SET VAL = ?
              WHERE NAME = ? '''
    cur = conn.cursor()
    cur.execute(sql, (value, flagName, ))
    conn.commit()

def get_flag(conn, flagName):
    cur = conn.cursor()
    cur.execute("SELECT * FROM flags WHERE NAME = ?", (flagName,))
    rows = cur.fetchall()

    return rows

def insert_flag(conn, flagName, value):
    sql = ''' INSERT INTO flags
              (NAME, VAL)
              VALUES (?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (flagName, value, ))
    conn.commit()

def add_arrival(conn, firstSpot, lastSpot):
    sql = ''' INSERT INTO arrivals
              (SCHEDULED_ARRIVAL, ACTUAL_ARRIVAL, DELAY_SEC, TIME_STOP_SEC)
              VALUES (?, ?, ?, ?) '''
    firstSpot_sec = time_str2s(firstSpot)
    lastSpot_sec = time_str2s(lastSpot)
    scheduled_sec = find_scheduled_arrival(firstSpot)
    scheduled_str = time_s2str(scheduled_sec)
    late_sec = time_sec_diff(scheduled_sec, firstSpot_sec)
    time_stop = time_str_diff(firstSpot, lastSpot)
    cur = conn.cursor()
    cur.execute(sql, (scheduled_str, firstSpot, late_sec, time_stop))
    conn.commit()

def time_str2s(time_str):
    time_arr = map(int, time_str.split(":"))
    return time_arr[0]*3600 + time_arr[1]*60 + time_arr[2]

def time_s2str(time_sec):
    hours = time_sec / 3600
    time_sec %= 3600
    minutes = time_sec / 60
    time_sec %= 60
    return str(hours)+":"+str(minutes)+":"+str(time_sec)

def time_str_diff(time1_str, time2_str):
    time_diff = time_str2s(time2_str) - time_str2s(time1_str)
    return min(time_diff, 3600*24-time_diff)

def time_sec_diff(time1_sec, time2_sec):
    time_diff = time2_sec - time1_sec
    return min(time_diff, 3600*24-time_diff)

def find_scheduled_arrival(time_str):
    time_sec = time_str2s(time_str)
    day_num = datetime.datetime.today().weekday()
    if day_num < 6:
        table = scheduled_arrivals_workdays
    elif day_num == 6:
        table = scheduled_arrivals_saturday
    else:
        table = scheduled_arrivals_sunday
    table_sec = []
    last_arrival = -1
    for hour in table:
        for minute in table[hour]:
            scheduled_arrival_sec = int(hour)*3600 + minute*60
            if scheduled_arrival_sec > time_sec and last_arrival == -1:
                last_arrival = scheduled_arrival_sec
    if last_arrival == -1:
        last_arrival = scheduled_arrival_sec
    return last_arrival
        
def insert_new_arrival(conn, arrival_str):
    if get_flag(conn, "LastSpot") == [] and get_flag(conn, "FirstSpot") == []:
        insert_flag(conn, "FirstSpot", arrival_str)
        insert_flag(conn, "LastSpot", arrival_str)
        return

    last_spot = get_flag(conn, "LastSpot")[0][2]
    if time_str_diff(arrival_str, last_spot) > maximum_stop:
        update_flag(conn, "FirstSpot", arrival_str)
        update_flag(conn, "LastSpot", arrival_str)
        add_arrival(conn, arrival_str, last_spot)
        update_flag(conn, "ArrivalOpen", "0")
    else:
        update_flag(conn, "LastSpot", arrival_str)
        update_flag(conn, "ArrivalOpen", "1")

def get_timediff(conn):
    ret = get_flag(conn, "StreamDelay")
    if ret == []:
        insert_flag(conn, "StreamDelay", str(70))
        return 70
    return int(ret[0][2])

def get_open(conn):
    ret = get_flag(conn, "ArrivalOpen")
    if ret == []:
        insert_flag(conn, "ArrivalOpen", "0")
        return 0
    return int(ret[0][2])

def check_arrival(conn, time_str):
    if get_open(conn) == 1:
        last_spot = get_flag(conn, "LastSpot")[0][2]
        if time_str_diff(arrival_str, last_spot) > maximum_stop:
            update_flag(conn, "ArrivalOpen", "0")
            add_arrival(conn, arrival_str, last_spot)
