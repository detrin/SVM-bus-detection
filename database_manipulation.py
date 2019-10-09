import sqlite3
from settings import *
import datetime
import json


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
    return str(hours).zfill(2)+":"+str(minutes).zfill(2)+":"+str(time_sec).zfill(2)

def time_str_diff(time1_str, time2_str):
    time1, time2 = time_str2s(time1_str), time_str2s(time2_str)
    time1, time2 = min(time1, time2), max(time1, time2)
    time_diff = time2 - time1
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
    scheduled_prev = 0
    for hour in table:
        for minute in table[hour]:
            scheduled_arrival_sec = int(hour)*3600 + minute*60
            if scheduled_arrival_sec > time_sec and last_arrival == -1:
                last_arrival = scheduled_prev
            scheduled_prev = scheduled_arrival_sec
    if last_arrival == -1:
        last_arrival = scheduled_arrival_sec
    return last_arrival

def find_next_arrival(time_str):
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
    arrival_open = get_open(conn)
    if time_str_diff(last_spot, arrival_str) > maximum_stop:
        first_spot = get_flag(conn, "FirstSpot")[0][2]
        update_flag(conn, "ArrivalOpen", "0")
        update_flag(conn, "FirstSpot", arrival_str)
        update_flag(conn, "LastSpot", arrival_str)
        add_arrival(conn, first_spot, last_spot)
        
    elif arrival_open == 1:
        update_flag(conn, "LastSpot", arrival_str)
        update_flag(conn, "ArrivalOpen", "1")
    else:
        update_flag(conn, "FirstSpot", arrival_str)
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
        if time_str_diff(last_spot, time_str) > maximum_stop:
            update_flag(conn, "ArrivalOpen", "0")
            first_spot = get_flag(conn, "FirstSpot")[0][2]
            add_arrival(conn, first_spot, last_spot)

def arrivals_to_json(conn, number_of_arrivals):
    sql = ''' 
            SELECT * FROM (
            SELECT * FROM arrivals ORDER BY ID DESC LIMIT ?)
            ORDER BY ID DESC '''
    cur = conn.cursor()
    cur.execute(sql, (number_of_arrivals*2, ))
    rows = cur.fetchall()
    summ = 0
    rows_dump = []
    for i in xrange(number_of_arrivals*2):
        dump_d = {}
        rows[i] = list(rows[i])
        delay_s = rows[i][3]
        rows[i][3] = time_s2str(rows[i][3])
        rows[i][3] = ":".join(rows[i][3].split(":")[1:])
        dump_d["scheduled_arrival"] = rows[i][1]
        dump_d["actual_arrival"] = rows[i][2]
        dump_d["delay"] = rows[i][3]
        if len(rows_dump) == 0 or rows_dump[-1] != dump_d:
            summ += delay_s
            rows_dump.append(dump_d)
    rows_dump = json.dumps(rows_dump[:number_of_arrivals])
    with open(PATH_JSON+"arrivals.json", "w") as f:
        f.write(rows_dump)

    avg = int(round(summ/float(number_of_arrivals)))
    avg_str = time_s2str(avg)
    avg_str = ":".join(avg_str.split(":")[1:])
    time_str = datetime.datetime.now()
    time_str = time_str.strftime('%H:%M:%S')
    arrival_next_sec = find_next_arrival(time_str)
    arrival_next_str = time_s2str(arrival_next_sec)
    arrival_delayed_sec = arrival_next_sec + avg
    arrival_delayed_str = time_s2str(arrival_delayed_sec)
    dump_d = {}
    with open(PATH_JSON+"estimate.json", "w") as f:
        dump_d["scheduled_arrival"] = arrival_next_str
        dump_d["estimated_arrival"] = arrival_delayed_str
        dump_d["estimated_delay"] = avg_str
        dump_d = json.dumps(dump_d)
        f.write(dump_d)

