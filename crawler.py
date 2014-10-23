import os
import threading
import argparse
from urllib.error import URLError
import time
from crawler_core import TaskWorker, TaskQueue
import urllib.request
import urllib.parse


__author__ = 'pahaz'
STAT_OUT = '[{i}] downloads: {dc} pop:{gt:0.5f} put:{pt:0.5f} work:{wt:0.5f}' \
           ' = {lt:0.5f}'


def save_binary_data_to_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)


class Urls(object):
    def __init__(self):
        self._store = set()
        self._lock = threading.Lock()

    def check_and_add(self, obj):
        self._lock.acquire()
        has = obj in self._store
        self._store.add(obj)
        self._lock.release()
        return has


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
        print(depth, self.max_depth)
        if depth > self.max_depth:
            return []

        is_visited = self.urls.check_and_add(url)
        if is_visited:
            return []

        try:
            u_open = urllib.request.urlopen(url)
            u_data = u_open.read()
        except (URLError, ValueError) as e:
            self.log("[{i}] Bead url {0} - {1}"
                     .format(url, repr(e), i=self.index))
            return []

        url_parsed = urllib.parse.urlparse(url)
        f_path = self.make_file_path(url)
        save_binary_data_to_file(f_path, u_data)

        return []

    def make_file_path(self, url):
        file_name = urllib.parse.quote(url, safe='')
        file_path = os.path.join(self.download_dir, file_name)
        return file_path


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
    _urls = Urls()
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
            gt=downloader.wait_get_time,
            pt=downloader.wait_put_time,
            wt=downloader.working_time,
            dc=downloader.work_done_counter,
            lt=downloader.all_live_time
        ))
