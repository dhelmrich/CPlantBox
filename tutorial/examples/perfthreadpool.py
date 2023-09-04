from concurrent.futures import ThreadPoolExecutor
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
def run_example_vis_performance():
  # global time list
  global time_list
  # get the time
  runtime = time.time()
  # spawn in this process without stdout and stderr
  os.system("python3 example_vis_performance.py > /dev/null 2>&1")
  # get the time
  runtime = time.time() - runtime
  time_list.append(runtime)
#enddef

n = 1000

#  function to fill the CPU with the run_example_vis_performance coroutine
with ThreadPoolExecutor(max_workers=cpu_count) as executor:
  for i in range(n):
    executor.submit(run_example_vis_performance)
  #endfor

# print the total runtime
print("Total runtime: ", str(time.time() - start_time), " on CPU count: ", str(cpu_count), " for ", str(n), " runs.")
time_list = np.array(time_list)
# print the average runtime
print("Average runtime: ", np.mean(time_list))
# print the standard deviation of the runtime
print("Standard deviation: ", np.std(time_list))
# print the minimum runtime
print("Minimum runtime: ", np.min(time_list))
# print the maximum runtime
print("Maximum runtime: ", np.max(time_list))