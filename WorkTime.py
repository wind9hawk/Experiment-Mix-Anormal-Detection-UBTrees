# coding:utf-8
# 为了避免朝九晚五的死板上班时间，特在Normal时段统计分析用户的正常时间

import os
import sys
import numpy as np

# 上班时间以半小时为一个精度，如8：00-8：30-9：00，


# 定义一个时间提取函数
def Extract_Date(date):
    # 01/02/2010 02:19:18
    year = date[6:10]
    month = date[0:2]
    day = date[3:5]
    hour = date[11:13]
    minute = date[14:16]
    seconds = date[17:]
    # 字符串类型用于比价是否存在，float后用于比较时间先后
    return year, month, day, hour, minute,  seconds

# print os.listdir(r'CERT4.2_Daily_Insiders')

# 定义一个work hours提取函数
def Ext_Work_Hours(user_id, DirPath):
    # DirPath = r'H:\CERT_Result\Experiment\Experiment-Mix-Anormal Detection-UBTrees\CERT4.2_Daily_Insiders'
    UserPath = DirPath+ '\\' + user_id
    MonthPath = UserPath + '\\' + os.listdir(UserPath)[0]
    print MonthPath, '\n'
    WorkOn_Hours = []
    WorkOff_Hours = []
    for file in os.listdir(MonthPath):
        filePath = MonthPath +'\\' + file
        # logon,AAF0535,PC-2408,Logon,01/04/2010 08:56:00
        # logon,AAF0535,PC-2408,Logoff,01/04/2010 17:05:00
        f = open(filePath, 'r')
        for line in f.readlines():
            line_lst = line.strip('\n').strip(',').split(',')
            if line_lst[0] == 'logon':
                year, month, day, hour, minute, seconds = Extract_Date(line_lst[-1])
                # 计算上班与下班时间只记录小时：分钟
                if line_lst[3] == 'Logon':
                    On_time = []
                    On_time.append(float(hour))
                    On_time.append(float(minute))
                    WorkOn_Hours.append(On_time)
                    continue
                if line_lst[3] == 'Logoff':
                    Off_time = []
                    Off_time.append(float(hour))
                    Off_time.append(float(minute))
                    WorkOff_Hours.append(Off_time)
                    continue
            else:
                continue
        f.close()
    WorkOn_Hours.sort()
    WorkOff_Hours.sort()
    print 'WorkOn : ', WorkOn_Hours, '\n'
    print 'WorkOff: ', WorkOff_Hours, '\n'
    # 正常工作范围为上下班时间左右浮动0.5小时
    WorkOn_Time = 0.0
    WorkOff_Time = 0.0
    for time in WorkOn_Hours:
        WorkOn_Time += time[0] * 60 + time[1]
    for time in WorkOff_Hours:
        WorkOff_Time += time[0] * 60 + time[1]
    # 分钟计算应以60为基本单位
    WorkOn_Clock = WorkOn_Time / len(WorkOn_Hours) - 30
    WorkOff_Clock = WorkOff_Time / len(WorkOff_Hours) + 30
    return  WorkOn_Clock, WorkOff_Clock
# 结果示例：
# WorkOn Clock is  509.55 8.4925
# WorkOff Clock is  1053.2 17.5533333333







