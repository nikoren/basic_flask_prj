import os, sys

# search for modules in current directory
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(file_dir)

from datetime import datetime
import clients, parsers
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count


def main():

    number_of_threads = 10
    bit2c_client = clients.Bit2c()
    bit2c_parser = parsers.Bit2c()

    pool = ThreadPool(processes=max(cpu_count()-1, 1))
    async_results = {}
    for i in range(number_of_threads):
        async_results[i] = pool.apply_async(bit2c_client.get_tickers)
        print "Starting new thread {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # print "Doing other stuff..."
    # pool.close()
    # pool.join()
    # print "All finished {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # print [bit2c_parser.parse_tickers(async_results[i].get())
    #        for i in range(number_of_threads)]

    finished  = [False  for i in range(number_of_threads)]
    while False in finished:
        for i in async_results:
            if finished[i] == False:
                if async_results[i].ready():
                    print bit2c_parser.parse_tickers(async_results[i].get())
                    print "Another thread finished {}\n\n\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    finished[i] = True
