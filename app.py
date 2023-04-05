import time
import sys
import threading
class TaskQueue:
    def __init__(self):
        """
        Constructor method that initializes the class attributes.
        """
        self.tasks = []
        self.lock = threading.Lock()
        self.tasks = []
        self.lock = threading.Lock()
        self.current_task = None
        self.previous_task = None
        self.next_task = None

    def add_task(self, task, priority=0, interval=None):
        """
        Method to add a new task to the queue.

        Parameters:
        task (function): the task to be added, which must be a callable function.
        priority (int): an optional priority (default is 0) to determine the order in which the task should be executed.
        interval (float): an optional interval (default is None) to specify how often the task should be executed.

        If interval is specified, the task will be executed repeatedly at the specified interval.
        """
        with self.lock:
            if not self.tasks:
                self.tasks.append((priority, task, interval, time.time()))
            else:
                for i, (p, _, _, _) in enumerate(self.tasks):
                    if priority > p:
                        self.tasks.insert(i, (priority, task, interval, time.time()))
                        break
                else:
                    self.tasks.append((priority, task, interval, time.time()))
            self.next_task = self.tasks[0][1] if self.tasks else None

    def get_task(self):
        """
        Method to retrieve the next task in the queue.

        Returns:
        The next task to be executed, or None if there are no tasks left.
        """
        with self.lock:
            if self.tasks:
                self.previous_task = self.current_task
                self.current_task = self.next_task
                if self.next_task == self.tasks[-1][1]:
                    self.next_task = self.tasks[0][1]
                else:
                    index = next((i for i, (_, task, _, _) in enumerate(self.tasks) if task.__name__ == self.current_task.__name__), None)
                    if index is not None:
                        self.next_task = self.tasks[(index + 1) % len(self.tasks)][1]
                    else:
                        self.next_task = None
                return self.current_task
            else:
                return None
    def remove_task(self, task):
        """
        Method to remove a task from the queue.

        Parameters:
        task (function): the task to be removed, which must be a callable function.

        Returns:
        True if the task was removed, or False if the task was not found.
        """
        with self.lock:
            index = next((i for i, (_, t, _, _) in enumerate(self.tasks) if t.__name__ == task.__name__), None)
            if index is not None:
                self.tasks.pop(index)
                return True
            else:
                return False
            
    def remove_all_tasks(self):
        """
        Method to remove all tasks from the queue.
        """
        with self.lock:
            self.tasks = []
            self.current_task = None
            self.previous_task = None
            self.next_task = None

    def log(self):
        """
        Method to print the current state of the queue.
        """
        print(f"Current task: {self.current_task.__name__ if self.current_task else None}")
        print(f"Previous task: {self.previous_task.__name__ if self.previous_task else None}")
        print(f"Next task: {self.next_task.__name__ if self.next_task else None}")
        print(f"Tasks: {', '.join([task.__name__ for _, task, _, _ in self.tasks])}\n")


    def run(self):
        """
        Method to execute the tasks in the queue.

        The method runs indefinitely until it is interrupted by the user with a KeyboardInterrupt.
        """
        try:
            while True:
                task = self.get_task()
                self.log()
                if task:
                    task()
                time.sleep(0.1)  # Add a small delay to reduce CPU usage
        except KeyboardInterrupt:
            sys.exit()

    @staticmethod
    def run_schedules(tasks):
        """
        Static method to run a set of tasks using a TaskQueue object.
        `Parameters`:
        tasks (dict): a dictionary that maps the name of the task to a dictionary containing the function to be executed, its priority, and an optional interval.
        The method creates a new instance of the TaskQueue class, adds the tasks to the queue, and executes them in order of priority.
        # Example:

        tasks = {
            "task1": {
                "task": lambda: print("task1 executed"),
                "priority": 0,
                "interval": 1
            },
            "task2": {
                
                "task": lambda: print("task2 executed"),
                "priority": 1,
                "interval": 2
            },
        }
        \n
        TaskQueue.run_schedules(tasks)
        """
        task_queue = TaskQueue()
        for name, task in tasks.items():
            if isinstance(task, dict) and "task" in task and callable(task["task"]) and "priority" in task and isinstance(task["priority"], int) and "interval" in task and (task["interval"] is None or isinstance(task["interval"], (int, float))):
                # print(f"Adding task {name}: function={task['task'].__name__}, priority={task['priority']}, interval={task['interval']}".center(80, "*"))
                task_queue.add_task(task["task"], priority=task["priority"], interval=task.get("interval"))
            else:
                raise ValueError(f"Invalid task {name}: {task}")
        task_queue.run()

def task1():
    print("task1 executed")
    time.sleep(8)

def task2():
    print("task2 executed")
    time.sleep(4)

def main():
    tasks = {
        "task1": {
            "task":     task1,
            "priority": 0,
            "interval": 8
        },
        "task2": {
            "task": task2,  # Add a small delay to reduce CPU usage,
            "priority": 1,
            "interval": 4
        },
    }
    TaskQueue.run_schedules(tasks)

if __name__ == "__main__":
    main()