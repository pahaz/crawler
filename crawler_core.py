from collections import deque
import threading
import time
import sys
import traceback

__author__ = 'pahaz'


class TaskWorker(threading.Thread):
    def __init__(self, index, task_queue, stop_event=None, is_debug=False):
        if not stop_event:
            stop_event = threading.Event()

        self.task_queue = task_queue
        self.work_done_counter = 0
        self.getting_work_time = 0.0
        self.working_with_result_time = 0.0
        self.working_time = 0.0
        self.full_working_time = 0.0
        self.is_debug = is_debug
        self.stop_event = stop_event
        self.index = index
        super().__init__(name="worker-" + str(index), daemon=True)

    def run(self):
        start_t = time.time()
        self.log("{t:0.5f} [{i}] start"
                 .format(i=self.index, t=start_t))
        try:
            while not self.stop_event.is_set():
                t1 = time.time()

                self.log("{t:0.5f} [{i}] want get work"
                         .format(i=self.index, t=t1))
                try:
                    task = self.task_queue.pop_front()
                except TaskQueueMaxPop:
                    raise

                t2 = time.time()

                self.log("{t:0.5f} [{i}] get work and start working"
                         .format(i=self.index, t=t2))

                result = self.do_work(task)

                self.task_queue.done()

                t3 = time.time()

                self.log("{t:0.5f} [{i}] work completed (done); start "
                         "do_something_with_work_result()"
                         .format(i=self.index, t=t3))
                self.work_done_counter += 1

                # ** WARNING ** it may be deadlock.
                # Case: `result` is new tasks and `task_queue` has max_size!
                #       When all workers try add new task in full queue they
                #       must wait when queue is free.
                #       (0 workers do work, all do push)
                # HFix: You can do push in other thread or use infinity
                #       queue ..
                self.do_something_with_work_result(result)

                t4 = time.time()

                self.log("{t:0.5f} [{i}] do_something_with_work_result "
                         "completed"
                         .format(i=self.index, t=t4))
                self.getting_work_time += t2 - t1
                self.working_time += t3 - t2
                self.working_with_result_time += t4 - t3
        except TaskQueueMaxPop:
            self.log("{t:0.5f} [{i}] max pop queue"
                     .format(i=self.index, t=time.time()))
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = ''.join(traceback.format_exception(exc_type, exc_value,
                                                    exc_traceback))
            self.log("{t:0.5f} [{i}] TERMINATED: {0}: \n{1}"
                     .format(repr(e), tb, i=self.index, t=time.time()))
        finally:
            end_t = time.time()
            self.full_working_time = end_t - start_t
            self.log("{t:0.5f} [{i}] stop"
                     .format(i=self.index, t=end_t))

    def log(self, msg):
        if self.is_debug:
            print(msg)

    def do_work(self, task):
        """
        Do main work

        Example:

            def do_work(self, task):
                time.sleep(0.100)
                return [task, task]

        :param task: queue task object
        :return: result (it may be new task list) used for
        `do_something_with_work_result` function
        """
        time.sleep(0.100)
        return [task, task]

    def do_something_with_work_result(self, result):
        """
        Do other work with `do_work` result

        :param result:
        :return:
        """
        if not result:
            return

        try:
            for new_task in result:
                # May be deadlock warning!
                self.task_queue.push_back(new_task)
        except TaskQueueMaxPush:
            pass


# ##### #
# QUEUE #
# ##### #


class TaskQueueMaxPush(Exception):
    pass


class TaskQueueMaxPop(Exception):
    pass


class TaskQueue(object):
    def __init__(self, max_queue_size=-1, max_count_of_done_works=-1):
        if not isinstance(max_queue_size, int) or max_queue_size < -1:
            raise TypeError('`max_queue_size` must be >= 0')
        if not isinstance(max_count_of_done_works, int) \
                or max_count_of_done_works < -1:
            raise TypeError('`max_tasks` must be >= 0')

        self.queue = deque()
        self.count_of_done = max_count_of_done_works
        self.count_of_push = max_count_of_done_works
        self.count_of_pop = max_count_of_done_works
        self.max_queue_size = max_queue_size
        self.lock = lock = threading.Lock()
        self._not_empty = threading.Condition(lock)
        self._not_full = threading.Condition(lock)
        self._all_done = threading.Condition()
        self.finish = threading.Event()

    def size(self):
        with self.lock:
            return len(self.queue)

    def join(self, timeout=None):
        with self._all_done:
            self._all_done.wait(timeout)

    def push_back(self, task):
        # print('push_back lock 0')
        with self._not_full:
            self._check_push()

            # print('push_back lock 1')
            if self.max_queue_size:
                if self.max_queue_size == len(self.queue):
                    # print('push_back wait 0')
                    self._not_full.wait()
                    # print('push_back wait 1')

            self.queue.append(task)
            self._not_empty.notify()

    def pop_front(self):
        # print('get lock 0')
        with self._not_empty:
            self._check_pop()

            # print('get lock 1')
            if 0 == len(self.queue):
                # print('get white 0')
                self._not_empty.wait()
                # print('get white 1')

            task = self.queue.popleft()
            self._not_full.notify()
            return task

    def done(self):
        with self._all_done:
            if self.count_of_done == -1:
                return

            if self.count_of_done - 1 > 0:
                self.count_of_done -= 1
            elif self.count_of_done - 1 == 0:
                self.count_of_done = 0
                self._all_done.notify_all()
                self.finish.set()
            else:
                raise TypeError("Max done() call")

    def _check_push(self):
        with self._all_done:
            if self.count_of_push == -1:
                return

            if self.count_of_push - 1 >= 0:
                self.count_of_push -= 1
            else:
                raise TaskQueueMaxPush

    def _check_pop(self):
        with self._all_done:
            if self.count_of_pop == -1:
                return

            if self.count_of_pop - 1 >= 0:
                self.count_of_pop -= 1
            else:
                raise TaskQueueMaxPop
