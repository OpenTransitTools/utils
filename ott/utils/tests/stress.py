"""
this module can be used to stress test an app
provide a method that does something (like curl a URL), and return a boolean indicating success
:adapted from: https://systemweakness.com/stress-testing-a-graphql-endpoint-with-python-script-c9852b40a084
"""

import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor


# globals used below
success_counter = 0
fail_counter = 0
custom_query_method = None
lock = threading.Lock()
exit_flag = threading.Event()


def execute_query(query):
    global success_counter, fail_counter
    status = query()
    if status is True:
        with lock:
            success_counter += 1
    else:
        with lock:
            fail_counter += 1


def run_query():
    while not exit_flag.is_set():
        with lock:
            print(".", end="", flush=True)
        execute_query(custom_query_method)


def stress_main(query_method):
    # prompt the user for the number of threads
    num_threads = int(input("Enter the number of threads: "))
    start_time = time.perf_counter()

    global custom_query_method
    custom_query_method = query_method

    # create and start the worker threads
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=run_query)
        thread.start()
        threads.append(thread)

    try:
        while True: # keep the main thread alive until interrupted
            pass
    except KeyboardInterrupt:
        print("Interrupt signal received. Stopping...")
        exit_flag.set()
        for thread in threads:
            thread.join()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print()
        print(f"Successes: {success_counter:>12}")
        print(f"Failures:  {fail_counter:>12}")
        print(f"Elapsed time: {elapsed_time:.4f} seconds")
        print()


def main():
    def simple_example_query():
        import random
        return random.random() > 0.1
    stress_main(simple_example_query)


if __name__ == "__main__":
    main()
