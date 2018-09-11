# coding:utf-8

# 本模块主要功能是统计分析70个攻击用户的检测效果，其中依据CERT4.2-2009-12-4Results.csv分类统计
# Recall/TPR/FPR
import os
import sys

# 定义一个函数分类统计Recall/TPR/FPR
def Classify_Check(Insiders_lst, Results_lst, f):
    Recall_Rate = 0.0
    TP_Rate = 0.0
    FP_Rate = 0.0

    Cnt_Insiders_Days_Sum = 0.0
    Cnt_Normal_Days_Sum = 0.0
    Cnt_TP_Days_Sum = 0.0
    Cnt_FP_Days_Sum = 0.0


    for usr in Insiders_lst:
        # print line, '\n'
        for line in Results_lst:
            line_lst = line.strip('\n').strip(',').split(',')
            # AAF0535,27,117,0,0,
            if line_lst[0] == usr:
                Cnt_Insiders_Days_Sum += float(line_lst[1])
                Cnt_Normal_Days_Sum += float(line_lst[2])
                Cnt_TP_Days_Sum += float(line_lst[3])
                Cnt_FP_Days_Sum += float(line_lst[4])
                for ele in line_lst:
                    f.write(str(ele))
                    f.write(',')
                f.write('\n')
                break
            else:
                continue
    if Cnt_Insiders_Days_Sum == 0:
        Recall_Rate = 'none'
    else:
        Recall_Rate = Cnt_TP_Days_Sum / Cnt_Insiders_Days_Sum
        TP_Rate = Cnt_TP_Days_Sum / (Cnt_TP_Days_Sum + Cnt_FP_Days_Sum)
        FP_Rate = Cnt_FP_Days_Sum / Cnt_Normal_Days_Sum
    return Recall_Rate, TP_Rate, FP_Rate


# 分别读入三类攻击场景的Insiders列表
Insiders_1_lst = []
Insiders_2_lst = []
Insiders_3_lst = []

for usr in os.listdir('r4.2-1'):
    print usr, '\n'
    Insiders_1_lst.append(usr[7:14])
for usr in os.listdir('r4.2-2'):
    Insiders_2_lst.append(usr[7:14])
for usr in os.listdir('r4.2-3'):
    Insiders_3_lst.append(usr[7:14])

print '第一类攻击场景有：', len(Insiders_1_lst), Insiders_1_lst, '\n'
print '第二类攻击场景有：', len(Insiders_2_lst), Insiders_2_lst, '\n'
print '第三类攻击场景有：', len(Insiders_3_lst), Insiders_3_lst, '\n'

f = open('CERT4.2-2009-12-4Results.csv', 'r')
f_lst = f.readlines()
f.close()

f_write = open('CERT4.2-2009-12-4Results_ByOrder.csv', 'w')
Recall_Rate, TPR, FPR = Classify_Check(Insiders_1_lst, f_lst, f_write)
print '第一类攻击检测效果为：\n'
print 'Recall Rate is ', Recall_Rate, '\n'
print 'TPR is ', TPR, '\n'
print 'FPR is ', FPR, '\n'

Recall_Rate, TPR, FPR = Classify_Check(Insiders_2_lst, f_lst, f_write)
print '第二类攻击检测效果为：\n'
print 'Recall Rate is ', Recall_Rate, '\n'
print 'TPR is ', TPR, '\n'
print 'FPR is ', FPR, '\n'

Recall_Rate, TPR, FPR = Classify_Check(Insiders_3_lst, f_lst, f_write)
f_write.close()
print '第三类攻击检测效果为：\n'
print 'Recall Rate is ', Recall_Rate, '\n'
print 'TPR is ', TPR, '\n'
print 'FPR is ', FPR, '\n'
