""" script that runs a task on as many workers as there are logical cores """
import asyncio
import time
import os
import numpy as np

# check number of available cores on the computer
cpu_count = os.cpu_count()

# global time list
time_list = []

# measure the total runtime
start_time = time.time()

# setup a coroutine that calls the example_vis_performance.py script
async def run_example_vis_performance():
  # global time list
  # get the time
  runtime = asyncio.get_event_loop().time()
  # spawn in this process because it is a blocking call
  proc = await asyncio.create_subprocess_exec(
    'python3', 'example_vis_performance.py',
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE)
  # wait for the subprocess to finish
  stdout, stderr = await proc.communicate()
  # get the time
  runtime = asyncio.get_event_loop().time() - runtime
  return runtime
#enddef

#  function to fill the CPU with the run_example_vis_performance coroutine
async def fill_cpu ( target_num_generated : int, concurrent = True ):
  global cpu_count, time_list
  # fill the CPU with the run_example_vis_performance coroutine
  if not concurrent:
    for i in range(target_num_generated):
      await run_example_vis_performance()
    #endfor
    return
  #endif
  tasks = []
  for i in range(target_num_generated):
    task = asyncio.create_task(run_example_vis_performance())
    tasks.append(task)
  #endfor
  # wait for all tasks to finish
  await asyncio.gather(*tasks)
  # extract times from the tasks
  return tasks
#enddef


# run the coroutine
async def main():
  global cpu_count, time_list
  """ run the task_wait_random coroutine """
  # await the task_wait_random coroutine
  n = 100
  tasks = await fill_cpu(n)
  # get the times from the tasks
  for task in tasks:
    time_list.append(task.result())
  #endfor

# run the main coroutine
if __name__ == "__main__":
  # run the main coroutine
  asyncio.run(main())
  # print the total runtime
  print("Total runtime: ", time.time() - start_time, " with ", cpu_count, " cores and ", n, " tasks.")
  # time list as numpy array
  time_list = np.array(time_list)
  # print the mean time
  print("Mean time: ", np.mean(time_list))
  # print the standard deviation
  print("Standard deviation: ", np.std(time_list))
  # print the minimum time
  print("Minimum time: ", np.min(time_list))
  # print the maximum time
  print("Maximum time: ", np.max(time_list))