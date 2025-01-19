import multiprocessing
import os
import fasteners
# python -m timeit -s "import ex1_lock" "ex1_lock.run_workers()"
# 400ms


MAX_COUNT_PER_PROCESS = 1000
FILENAME = "count.txt"


def work_smaller_chunks(filename, max_count):
    @fasteners.interprocess_locked('/tmp/tmp_lock')
    def work_write(filename):
        f = open(filename, "r")
        try:
            nbr = int(f.read())
        except ValueError as err:
            print("File is empty, starting to count from 0, error: " + str(err))
            nbr = 0
        #print(os.getpid())
        f = open(filename, "w")
        f.write(str(nbr + 1) + '\n')
        f.close()

    for n in range(max_count):
        work_write(filename)

@fasteners.interprocess_locked('/tmp/tmp_lock')
def work(filename, max_count):
    for n in range(max_count):
        f = open(filename, "r")
        try:
            nbr = int(f.read())
        except ValueError as err:
            print("File is empty, starting to count from 0, error: " + str(err))
            nbr = 0
        f = open(filename, "w")
        f.write(str(nbr + 1) + '\n')
        f.close()


def run_workers():
    NBR_PROCESSES = 4
    total_expected_count = NBR_PROCESSES * MAX_COUNT_PER_PROCESS
    print("Starting {} process(es) to count to {}".format(NBR_PROCESSES, total_expected_count))
    # reset counter
    f = open(FILENAME, "w")
    f.close()

    processes = []
    for process_nbr in range(NBR_PROCESSES):
        p = multiprocessing.Process(target=work, args=(FILENAME, MAX_COUNT_PER_PROCESS))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("Expecting to see a count of {}".format(total_expected_count))
    print("{} contains:".format(FILENAME))
    os.system('more ' + FILENAME)


if __name__ == "__main__":
    run_workers()
