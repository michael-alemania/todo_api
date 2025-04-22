import uuid
import random

num_tasks = 1_000_000
batch_size = 10000

with open("tasks.sql", "w") as f:
    f.write("BEGIN;\n")
    position = 0.0
    for i in range(1, num_tasks + 1, batch_size):
        end = min(i + batch_size - 1, num_tasks)
        f.write("INSERT INTO tasks (id, title, description, done, position) VALUES\n")
        values = []
        for j in range(i, end + 1):
            task_id = uuid.uuid4() 
            title = f"Task #{j}"
            description = f"This is the description for task #{j}"
            done = random.choice(["true", "false"])
            values.append(f"('{task_id}', '{title}', '{description}', {done}, {position:.2f})")
            position += 1.0
        f.write(",\n".join(values))
        f.write(";\n")
    f.write("COMMIT;\n")
