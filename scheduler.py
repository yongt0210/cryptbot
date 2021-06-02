import schedule
import os
import time

def restart():
    os.system("kill -9 $(ps -ef |grep python |grep index |awk '{print $2}')")
    time.sleep(3)

    os.system('python /workspace/coinbot/index.py &')

schedule.every().day.at('00:00').do(restart)

while True:
    schedule.run_pending()
    time.sleep(1)