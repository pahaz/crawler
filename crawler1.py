from html.parser import HTMLParser
import os
import threading
import argparse
from urllib.error import URLError
import time
from crawler_core import TaskWorker, TaskQueue
import urllib.request
import urllib.parse
from crawler_util import save_binary_data_to_file, get_links, \
    UrlThreadSafeStore


__author__ = 'pahaz'
STAT_OUT = '[{i}] downloads: {dc} pop:{gt:0.5f} put:{pt:0.5f} work:{wt:0.5f}' \
           ' = {lt:0.5f}'


class Downloader(TaskWorker):
    def __init__(self, urls, max_depth, download_dir, index, task_queue,
                 stop_event=None,
                 is_debug=False):
        if not isinstance(max_depth, int) or max_depth <= 0:
            raise TypeError('`max_depth` must be > 0')

        self.urls = urls
        self.max_depth = max_depth
        self.download_dir = download_dir
        super().__init__(index, task_queue, stop_event, is_debug)

    def do_work(self, task):
        url, depth = task
        if depth > self.max_depth:
            return []

        is_visited = self.urls.check_and_add(url)
        if is_visited:
            return []

        tx1 = tx2 = tx3 = t0 = time.time()
        self.log("{t:0.5f} [{i}] START. URL {0}"
                 .format(url, i=self.index, t=t0))
        try:
            b_data, b_head, headers = self.do_request(url)

            tx1 = time.time()

            f_data_path = self.get_file_data_path(url)
            self.do_save_file_data(url, f_data_path, b_data)

            f_head_path = self.get_file_head_path(url)
            self.do_save_file_data(url, f_head_path, b_head)

            tx2 = time.time()

            urls = get_links(url, headers, b_data)

            tx3 = time.time()

            if self.max_depth <= depth + 1:
                return []
            return [(u, depth + 1) for u in urls]
        except Exception as e:
            self.log("[{i}] PROBLEM with URL {0} : {e}"
                     .format(url, e=repr(e), i=self.index))
        finally:
            t1 = time.time()
            dt = (t1 - t0) * 1000.0
            t_request = (tx1 - t0) * 1000.0
            t_save = (tx2 - tx1) * 1000.0
            t_parse = (tx3 - tx2) * 1000.0
            self.log("{t:0.5f} [{i}] STOP. WORKING {dt:0.0f}ms "
                     "[REQUEST: {1:0.0f}ms SAVE: {2:0.0f}ms PARSE: {3:0.0f}ms]"
                     " WITH URL {0}"
                     .format(url, t_request, t_save, t_parse, i=self.index,
                             t=t1, dt=dt))

    def get_file_data_path(self, url):
        file_name = urllib.parse.quote(url, safe='') + '.html'
        file_path = os.path.join(self.download_dir, file_name)
        return file_path

    def get_file_head_path(self, url):
        return self.get_file_data_path(url) + '.header.txt'

    def do_save_file_data(self, url, file_path, b_data):
        try:
            save_binary_data_to_file(file_path, b_data)
        except OSError as e:
            self.log("[{i}] File save error from url {1} (name {0}) : {e}"
                     .format(file_path, url, e=repr(e), i=self.index))
            raise

    def do_request(self, url):
        try:
            u_open = urllib.request.urlopen(url)
            headers = [(h.lower(), v) for h, v in u_open.getheaders()]
            b_data = u_open.read()
        except Exception as e:
            self.log("[{i}] Bead url {0} : {e}"
                     .format(url, e=repr(e), i=self.index))
            raise

        b_head = '\n'.join(map(lambda x: x[0] + ': ' + x[1], headers)).encode()
        return b_data, b_head, headers


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Web graph downloader')
    parser.add_argument('url', type=str,
                        help='Start URL')
    parser.add_argument('max_depth', type=int,
                        help='Max graph depth')
    parser.add_argument('max_downloads', type=int,
                        help='Max count of download pages')
    parser.add_argument('download_dir', type=str,
                        help='Path to download dir')

    parser.add_argument('--debug', action='store_true',
                        help='Debug flag (default 0)')
    parser.add_argument('--threads', action='store', default=2, type=int,
                        help='Number of download threads (default 20)')

    args = parser.parse_args()

    if not os.path.isdir(args.download_dir):
        raise argparse.ArgumentError('download_dir', 'Path is not dir')

    # check first url
    # python crawler.py qeqweqwe 2 2 . --debug --thread 3
    _urls = UrlThreadSafeStore()
    _stop = threading.Event()
    _task_queue = TaskQueue(max_queue_size=-1,
                            max_count_of_done_works=args.max_downloads)
    _task_queue.push_back(
        (args.url, 0)
    )

    _task_workers = []
    for index in range(args.threads):
        # p = args.download_dir
        downloader = Downloader(_urls, args.max_depth, args.download_dir,
                                index,
                                _task_queue, _stop,
                                is_debug=args.debug)
        _task_workers.append(downloader)
        downloader.start()

    # _task_queue.join()
    try:
        while True:
            time.sleep(1)
            if _task_queue.finish.is_set():
                print('WORK FINISHED!')
                break
            if all(x._is_stopped for x in _task_workers):
                print('ALL WORKERS STOPPED!')
                break
    except KeyboardInterrupt:
        pass

    print('TasksQueue: size({0}) {2}/{1}'.format(_task_queue.size(),
                                                 _task_queue.count_of_push,
                                                 _task_queue.count_of_done))
    _stop.set()
    for downloader in _task_workers:
        # print(tasks.not_full._waiters)
        # print(tasks.not_empty._waiters)
        print(downloader)  # .join()

    for downloader in _task_workers:
        print(STAT_OUT.format(
            i=downloader.index,
            gt=downloader.getting_work_time,
            pt=downloader.working_with_result_time,
            wt=downloader.working_time,
            dc=downloader.work_done_counter,
            lt=downloader.full_working_time
        ))
