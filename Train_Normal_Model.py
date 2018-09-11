# coding:utf-8
# 本模块的主要任务是，对于基础异常检测而言，通过用户第一个月的数据训练得到Normal_Records，并生成每天的Normal_Features
# 核心工作是生成第一个月所有天对应的行为特征，由于CERT4.2中部分审计数据仅审计一种行为，故usr-activity-attribute的模式中
# activity可能针对不同的域会省略，导致匹配模式仅有四种
# 行为特征结构：
# 第一层：域类型，即登录、文件、邮件、HTTP、USB
# 第二层：针对每个域类型，早于正常开始工作时间，正常工作时间范围内，晚于正常下班时间
# 第三层：若对于2类属性，有四种模式；对于邮件而言，因为属性部分补充了附件，故有8种

# 必要的域记录格式：
# CERT4.2: logon + user + pc + activity + date
# 4.2: file + user + pc + filename + date
# 4.2-email: email + user + pc + from + to + size + attachment_count + date
# 4.2-http: http + user + pc + url + date
# 4.2-device: device + user + pc + activity + date

#
#
#
# 下面开始训练模块的编写，该模块最终要通过import形式导入到Train模块

import os
import sys

import WorkTime

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

# 定义一个函数通过读入的hour/minute来判断其是否早于/处于/晚于正常时间
# 0-过早，1-正常，2-过晚
def WorkTime_Segment(hour, minute, WorkOn_Time, WorkOff_Time):
    NowTime = float(hour) * 60 + float(minute)
    if NowTime < WorkOn_Time:
        return 0
    if NowTime >= WorkOn_Time and NowTime <= WorkOff_Time:
        return 1
    if NowTime > WorkOff_Time:
        return 2

# 由于列表的in操作无法分析子列表，如1 in [[1,2],3]为false，显然非我们这里所取的意思
def EleInList(ele, InList):
    # 判断ele是否在InList中出现过
    for x in InList:
        for y in x:
            if ele == y:
                return True
    return False

# 定义一个行为模式分析函数，输入记录与Normal_Records即可
# 第一天由于Normal_Records开始为空，因此有很多记录为“D-D”，无妨
def Match_Mode(line_lst, Normal_Records, Domain_type):
    # type用于表示不同的域类型，不同的域对应的特征数目不同
    # 返回模式字符串
    # CERT4.2: logon + user + pc + activity + date
    # 4.2: file + user + pc + filename + date
    # 4.2-email: email + user + pc + from + to + size + attachment_count + date
    # 4.2-http: http + user + pc + url + date
    # 4.2-device: device + user + pc + activity + date
    BMode = []
    if Domain_type == 'logon':
        if not EleInList(line_lst[2], Normal_Records):
            # pc匹配失败
            BMode.append('D')
            if not EleInList(line_lst[3], Normal_Records):
                BMode.append('D')
            else:
                BMode.append('S')
        else:
            BMode.append('S')
            # 此时因为pc已经匹配，因此需要在pc匹配的记录中继续进行匹配
            for record in Normal_Records:
                if record[0] != 'logon':
                    continue
                if record[2] == line_lst[2]:
                    if record[3] != line_lst[3]:
                        continue
                    else:
                        BMode.append('S')
                        break
            if len(BMode) < 2:
                BMode.append('D')
    # 4.2: file + user + pc + filename + date
    if Domain_type == 'file':
        if not EleInList(line_lst[2], Normal_Records):
            # pc匹配失败
            BMode.append('D')
            if not EleInList(line_lst[3], Normal_Records):
                BMode.append('D')
            else:
                BMode.append('S')
        else:
            BMode.append('S')
            # 此时因为pc已经匹配，因此需要在pc匹配的记录中继续进行匹配
            for record in Normal_Records:
                if record[0] != 'file':
                    continue
                if record[2] == line_lst[2]:
                    if record[3] != line_lst[3]:
                        continue
                    else:
                        BMode.append('S')
                        break
            if len(BMode) < 2:
                BMode.append('D')
    # 4.2-http: http + user + pc + url + date
    if Domain_type == 'http':
        if not EleInList(line_lst[2], Normal_Records):
            # pc匹配失败
            BMode.append('D')
            if not EleInList(line_lst[3], Normal_Records):
                BMode.append('D')
            else:
                BMode.append('S')
        else:
            BMode.append('S')
            # 此时因为pc已经匹配，因此需要在pc匹配的记录中继续进行匹配
            for record in Normal_Records:
                if record[0] != 'http':
                    continue
                if record[2] == line_lst[2]:
                    if record[3] != line_lst[3]:
                        continue
                    else:
                        BMode.append('S')
                        break
            if len(BMode) < 2:
                BMode.append('D')
    # 4.2-device: device + user + pc + activity + date
    if Domain_type == 'device':
        if not EleInList(line_lst[2], Normal_Records):
            # pc匹配失败
            BMode.append('D')
            if not EleInList(line_lst[3], Normal_Records):
                BMode.append('D')
            else:
                BMode.append('S')
        else:
            BMode.append('S')
            # 此时因为pc已经匹配，因此需要在pc匹配的记录中继续进行匹配
            for record in Normal_Records:
                if record[0] != 'device':
                    continue
                if record[2] == line_lst[2]:
                    if record[3] != line_lst[3]:
                        continue
                    else:
                        BMode.append('S')
                        break
            if len(BMode) < 2:
                BMode.append('D')
    # 4.2-email: email + user + pc + from + to + size + attachment_count + date
    if Domain_type == 'email':
        # 输入的line_lst仅为发送邮件
        if not EleInList(line_lst[2], Normal_Records):
            # pc匹配失败
            BMode.append('D')
            if not EleInList(line_lst[4], Normal_Records):
                # 收件人不在Normal列表里
                BMode.append('D')
                if not EleInList(line_lst[6], Normal_Records):
                    BMode.append('D')
                else:
                    # attachment存在
                    BMode.append('S')
            else:
                BMode.append('S')
                for record in Normal_Records:
                    if record[0] != 'email':
                        continue
                    if record[4] == line_lst[4]:
                        if record[6] != line_lst[6]:
                            continue
                        else:
                            BMode.append('S')
                            break
                if len(BMode) < 3:
                    BMode.append('D')
        BMode.append('S')
        for record in Normal_Records:
            if record[0] != 'email':
                continue
            if record[2] == line_lst[2]:
                if record[4] != line_lst[4]:
                    # print 'record is ', record, '\n'
                    # print 'line_lst is ', line_lst, '\n'
                    if record[6] != line_lst[6]:
                        continue
                    else:
                        BMode.append('D')
                        BMode.append('S')
                        break
                else:
                    BMode.append('S')
                    if record[6] != line_lst[6]:
                        continue
                    else:
                        BMode.append('S')
                        break
        if len(BMode) < 2:
            BMode.append('D')
            BMode.append('D')
    return BMode




# 定义分析第一个训练文件的特征提取函数
# 该函数返回第一天的行为特征以及第一天后的Normal_Records
def Extract_Normal_Features(user_id, f_lst, Normal_Records, WorkOn_Time, WorkOff_Time, User_M_Email):
    # 第一天的所有记录逐条分析
    # 每个记录都作为S-S-S/S-S记录即可
    # 具体计算时需要输入WorkOn_Time与WorkOff_Time
    # 假设正常工作时间范围相对稳定，因而只利用Normal时间段作为计算WorkOn_Time与WorkOff_Time

    # 定义行为特征
    # 对于Logon域而言，考虑pc + activity，共4种；
    # 对于File域而言，考虑pc + filename，因为默认都是copy行为，故也只有4种变化
    # 对于Email域而言，考虑pc + to + attachment，仅考虑用户发送的邮件，即有8种变化
    # 对于Http域而言，考虑pc + url，共4种；
    # 对于Device域而言，考虑pc + activity，共4种
    # 其中考虑时间的话，各自有3倍的特征数
    Day_Records = []
    # 初始化分域特征
    Logon_feats = [0] * 12
    File_feats= [0] * 12
    Email_feats = [0] * 24
    Http_feats = [0] * 12
    Device_feats = [0] * 12

    for ele in User_M_Email:
        if ele[0] == user_id:
            User_Email = ele[1]
            break
        else:
            User_Email = 'None'
            continue

    for line in f_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # 判断该条记录的类型，然后计入匹配的行为特征
        # 处理完后将该条记录追加到Normal_Records

        # 首先判断记录所处时间段
        year, month, day, hour, minute,  seconds = Extract_Date(line_lst[-1])
        # print hour, minute, '\n'
        # print 'line is ', line, '\t', line_lst[-1], '\n'
        TimeLabel = WorkTime_Segment(hour, minute, WorkOn_Time, WorkOff_Time)
        # CERT4.2: logon + user + pc + activity + date
        # 4.2: file + user + pc + filename + date
        # 4.2-email: email + user + pc + from + to + size + attachment_count + date
        # 4.2-http: http + user + pc + url + date
        # 4.2-device: device + user + pc + activity + date

        # 开始分析该条记录的行为模式（如S-S等）
        # 仅需要单独处理邮件的发件人信息
        # 需要使用User_Map_Email列表筛选发送邮件
        if line_lst[0] == 'email':
            if User_Email == 'None':
                continue
            if User_Email != line_lst[3]:
                continue
        BMode = Match_Mode(line_lst, Normal_Records, line_lst[0])

        # 模式编号
        # 对于四种模式而言
        # 0：S-S
        # 1：S-D
        # 2：D-D
        # 3：D-S
        # 对于八种模式而言
        # 0: S-S-S
        # 1: S-S-D
        # 2: S-D-D
        # 3: D-D-D
        # 4. D-D-S
        # 5. D-S-S
        # 6. S-D-S
        # 7. D-S-D

        FourModes = [['S', 'S'], ['S', 'D'], ['D','D'], ['D', 'S']]
        EightModes= [['S', 'S', 'S'], ['S', 'S', 'D'], ['S', 'D', 'D'], ['D', 'D', 'D'], ['D', 'D', 'S'], ['D', 'S', 'S'], ['S', 'D', 'S'], ['D', 'S', 'D']]
        if len(BMode) == 2:
            # TimeLabel:0-1-2
            EleIndex = TimeLabel * 4 + FourModes.index(BMode)
        if len(BMode) == 3:
            EleIndex= TimeLabel * 8 + EightModes.index(BMode)
        if line_lst[0] == 'logon':
            Logon_feats[EleIndex] += 1.0
        if line_lst[0] == 'file':
            File_feats[EleIndex] += 1.0
        if line_lst[0] == 'email':
            Email_feats[EleIndex] += 1.0
        if line_lst[0] == 'http':
            Http_feats[EleIndex] += 1.0
        if line_lst[0] == 'device':
            Device_feats[EleIndex] += 1.0
        Day_Records.append(line_lst)

    # 拼接成特征向量
    Day_Features = []
    Day_Features.append(Logon_feats)
    Day_Features.append(File_feats)
    Day_Features.append(Http_feats)
    Day_Features.append(Device_feats)
    Day_Features.append(Email_feats)

    return Day_Features, Day_Records
#
#
# 定义训练函数
def Train_Normal_Model(user_id, DirPath, Normal_Records, Normal_Features, User_M_Email):
    # 参数共同标记出训练数据来源
    # DirPath = r'H:\CERT_Result\Experiment\Experiment-Mix-Anormal Detection-UBTrees\CERT4.2_Daily_Insiders'
    # 首先明确表示出训练数据
    MonthPath = DirPath + '\\' + user_id
    FirstPath = os.listdir(MonthPath)[0]
    SecondPath = os.listdir(MonthPath)[1]

    # 默认是选择第一个月中的所有数据作为Normal
    NormalFilesPath = MonthPath + '\\' + FirstPath
    # 提取正常工作时间范围（依据场景分析，仅依靠第一个月计算）
    WorkOn_Time, WorkOff_Time = WorkTime.Ext_Work_Hours(user_id, DirPath)
    print 'WorkOn_Time, WorkOff_Time is ', WorkOn_Time, WorkOff_Time, '\n'
    Normal_Records = []
    Normal_Features = []
    Normal_Features_Ori_W = []
    for file in os.listdir(NormalFilesPath):
        # Normal_Features_Ori_W = []
        filePath = NormalFilesPath + '\\' + file
        f = open(filePath, 'r')
        f_lst = f.readlines()
        f.close()
        # 一个normal文件已经打开，并读入了列表
        # 输入该文件列表构建第一天的Normal_Records与Normal_Features
        # 处理函数为Extract_1st_Normal_Features
        Day_Features, Day_Records = Extract_Normal_Features(user_id, f_lst, Normal_Records, WorkOn_Time, WorkOff_Time, User_M_Email)
        Normal_Features.append(Day_Features)
        # print Normal_Features, '\n'
        tmp = []
        tmp.append(file)
        tmp.append(Day_Features)
        Normal_Features_Ori_W.append(tmp)
        # print Normal_Features_Ori_W, '\n'
        # sys.exit()
        for line in Day_Records:
            Normal_Records.append(line)
    print user_id, MonthPath, 'Normal Records read done...\n'
    return Normal_Features, Normal_Features_Ori_W, Normal_Records


#
#
#
#
#

# 测试程序
# sys.exit()
# user_id = 'AAF0535'
# DirPath = r'H:\CERT_Result\Experiment\Experiment-Mix-Anormal Detection-UBTrees\CERT4.2_Daily_Insiders'
# Normal_Records = []
# Normal_Features = []
# Normal_Features, Normal_Records = Train_Normal_Model(user_id, DirPath, Normal_Records, Normal_Features)
# print len(Normal_Features), '\t', Normal_Features[0], '\n'

