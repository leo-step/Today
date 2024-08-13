from concurrent.futures import ThreadPoolExecutor, as_completed
# import persistqueue
from tqdm import tqdm
from queue import Queue

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

            for future in tqdm(as_completed(futures), total=len(futures)):
                pass

        results = []
        while not self.out_queue.empty():
            results.append(self.out_queue.get())
        
        reduced = self.reduceF(results)

        return reduced