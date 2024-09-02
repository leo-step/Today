from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
# import persistqueue
from tqdm import tqdm
from queue import Queue
import time

class MapReduce:
    def __init__(self):
        # self.out_queue = persistqueue.FIFOSQLiteQueue('mrdata',
        #                     auto_commit=True, multithreading=True)
        self.out_queue = Queue()

    def get_items(self):
        return NotImplementedError

    def mapF(self, item):
        return NotImplementedError

    def mapF_helper(self, item):
        out = self.mapF(item)
        self.out_queue.put(out)

    def reduceF(self, results):
        return NotImplementedError

    def run(self, num_workers=8):
        items = self.get_items()
        futures = []

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for item in items:
                future = executor.submit(self.mapF_helper, item)
                futures.append(future)

            # Collect completed futures with a per-iteration timeout
            completed_count = 0
            total_futures = len(futures)

            while completed_count < total_futures:
                # Use a small timeout for each batch check
                timeout_per_batch = 240
                completed_futures = []

                try:
                    # Iterate over completed futures within the timeout period
                    for future in tqdm(as_completed(futures, timeout=timeout_per_batch), total=total_futures):
                        completed_futures.append(future)
                        completed_count += 1
                except TimeoutError:
                    # Silently ignore batch timeout; continue to collect results
                    pass

                # Remove completed futures from the futures list
                futures = [f for f in futures if f not in completed_futures]

        results = []
        while not self.out_queue.empty():
            results.append(self.out_queue.get())

        reduced = self.reduceF(results)

        return reduced
