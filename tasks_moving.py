tasks = []
all_tasks = [1, 2, 3, 2, 5]
for task in all_tasks:
    if task == 2:
        tasks.append(all_tasks.pop(all_tasks.index(task)))
print(all_tasks)
