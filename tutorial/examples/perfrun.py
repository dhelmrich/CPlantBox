""" script that runs a task on as many workers as there are logical cores """
import asyncio
import time
import os
import numpy as np
import mpi4py as mpi
from mpi4py import MPI

# check the number of MPI processes
comm = MPI.COMM_WORLD
comm_rank = comm.Get_rank()
comm_size = comm.Get_size()

# get the maximum plant count from the command line
import sys
n = 1000
print(sys.argv)
if len(sys.argv) > 1:
  n = int(sys.argv[1])
#endif

# divide the number of plants by the number of MPI processes
n = int(n / comm_size)

# check number of available cores on the computer
cpu_count = int(os.environ['LOCAL_NUM_CPUS']) if 'LOCAL_NUM_CPUS' in os.environ else 6

print("R", comm_rank, " - Size: ", comm_size, " CPU count: ", cpu_count, " for ", n, " runs, which is ", str(int(n / cpu_count)), " consequtive")

# global time list
time_list = []

# measure the total runtime
start_time = time.time()

capture_output = True

# setup a coroutine that calls the example_vis_performance.py script
async def run_example_vis_performance():
  global capture_output
  # global time list
  # get the time
  runtime = asyncio.get_event_loop().time()
  outpipe = asyncio.subprocess.PIPE if capture_output else asyncio.subprocess.DEVNULL
  # spawn in this process because it is a blocking call
  proc = await asyncio.create_subprocess_exec(
    "python","example_vis_performance.py",
    stdout=outpipe,
    stderr=outpipe)
  if capture_output:
    stdout, stderr = await proc.communicate()
  # get the time
  runtime = asyncio.get_event_loop().time() - runtime
  print("Task finished")
  return runtime
#enddef

#  function to fill the CPU with the run_example_vis_performance coroutine
async def fill_cpu ( target_num_generated : int, concurrent = True ):
  global cpu_count, time_list
  # fill the CPU with the run_example_vis_performance coroutine
  if not concurrent:
    for i in range(target_num_generated):
      runtime = await run_example_vis_performance()
      time_list.append(runtime)
    #endfor
    return
  #endif
  tasks = []
  # fill CPU with tasks in batches of cpu_count
  for i in range(cpu_count) :
    print("Creating CPU Task ", i)
    # create a task
    task = asyncio.create_task(run_example_vis_performance())
    # append the task to the list of tasks
    tasks.append(task)
  #endfor
  # wait for all tasks to finish
  await asyncio.gather(*tasks)
  # extract times from the tasks
  for task in tasks:
    timing_result = task.result()
    time_list.append(timing_result)
  #endfor
  # clear the list of tasks
  tasks.clear()
#enddef

# run the coroutine
async def main():
  global cpu_count, time_list, n
  """ run the task_wait_random coroutine """
  # await the task_wait_random coroutine
  await fill_cpu(n)
  # get the times from the tasks
  #for task in tasks:
  #  time_list.append(task.result())
  #endfor

# run the main coroutine
if __name__ == "__main__":
  # run the main coroutine
  asyncio.run(main())
  # print the total runtime
  print("R", comm_rank, ": Total runtime: ", time.time() - start_time, " with ", cpu_count, " cores and ", n, " tasks.")
  # time list as numpy array
  time_list = np.array(time_list)
  print("Time shape", time_list.shape)
  print("Time sum", np.sum(time_list))
  # print the mean time
  print("Mean time: ", np.mean(time_list))
  # print the standard deviation
  print("Standard deviation: ", np.std(time_list))
  # print the minimum time
  print("Minimum time: ", np.min(time_list))
  # print the maximum time
  print("Maximum time: ", np.max(time_list))
  np.savetxt("looptime_"+str(comm_rank)+".txt", time_list)
  exit(0)
  if comm_rank == 0:
    print("Rank: ", comm_rank, " Size: ", comm_size, " CPU count: ", cpu_count, " for ", n, " runs.")
    # get the times from the other processes
    print("Getting times from other processes...")
    for i in range(1, comm_size):
      time_list = np.append(time_list, comm.recv(source=i))
    #endfor
    print("Got times from other processes...")
    if len(time_list) == 0 :
      print("Error: time_list is empty.")
      exit(0)
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
    np.savetxt("times.txt", time_list)
  else:
    comm.send(time_list, dest=0)
  #endif
#endif