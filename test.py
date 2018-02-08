import sys
import time


def sec2time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def view_bar(num, total, st=time.clock()):
    rate = num / total
    rate_num = int(rate * 100)
    duration = int(time.clock() - st)
    remaining = int(duration * 100 / (0.01 + rate_num) - duration)
    r1 = '\r进度:{0}/{1}[{2}{3}]{4}%'.format(num, total, "=" * rate_num, " " * (100 - rate_num), rate_num)
    r2 = '\t持续时间:{0},剩余时间:{1}\n'.format(sec2time(duration), sec2time(remaining))
    sys.stdout.write(r1 + r2)
    sys.stdout.flush()


for i in range(100):
    view_bar(i, 100)
    time.sleep(2)
