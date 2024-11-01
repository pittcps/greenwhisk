import subprocess
import pandas as pd
import datetime
import asyncio
from time import sleep
import numpy as np


async def invoke_function(times, function_name):
    async def run_subprocess():
        print(f'Running subprocess for: {function_name}')
        await asyncio.create_subprocess_exec(
            "../bin/wsk", "action", "invoke", function_name, "--insecure", "--auth", "789c46b1-71f6-4ed5-8c54-816aa4f8c502:abczO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP"
        )

    tasks = []
    for i in range(times):
        tasks.append(asyncio.create_task(run_subprocess()))
        if i < times - 1:
            await asyncio.sleep(60 / times)
    await asyncio.gather(*tasks)

func_map = {
    0: 'test.js',
    1: 'test.py',
    2: 'test.rb'
}

np.random.seed(42)


async def main():
    print('Started Main')
    # df = pd.read_csv('medium-workload-function-trace.csv')
    # df = pd.read_csv('rare_3.csv')
    # df = pd.read_csv('high_65_1440.csv')
    # df = pd.read_csv('low_65_20.csv')
    # df = pd.read_csv('rep_65_20.csv')
    df = pd.read_csv('high-workload-function-trace.csv')
    apihost = "https://192.168.1.156:444"

    subprocess.run(["../bin/wsk", "property", "set", "--apihost", apihost])

    for _, row in df.iterrows():
        function_name = row['HashFunction']
        randFunc = np.random.randint(0, 3)
        row['FuncType'] = func_map[randFunc]
        subprocess.run(["../bin/wsk", "action", "create", function_name, func_map[randFunc], "--insecure","--timeout", "300000","--auth", "789c46b1-71f6-4ed5-8c54-816aa4f8c502:abczO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP"])

    start_min = 1

    for i in range(start_min, 11): # Change range for # of minutes
        currTime = datetime.datetime.now()
        coros = []
        for _, row in df.iterrows():
            if row[[f"{i}"]].iloc[0] > 0:
                print(f"Function {row['HashFunction']} sent for execution")
                coros.append(invoke_function(row[f"{i}"], row['HashFunction']))

        await asyncio.gather(*coros)

        timeNow = datetime.datetime.now()
        diff = timeNow - currTime
        rem_sleep = 60 - diff.seconds if diff.seconds <= 60 else 0
        sleep(rem_sleep)
        print(f"\nMin {i} over\n")

    print('Main over')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
