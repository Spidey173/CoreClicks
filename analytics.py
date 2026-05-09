import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

# ================================
# 1. GENERATE SAMPLE DATA
# ================================

# ----- Password Analysis -----
password_data = []
strength_levels = ['Weak', 'Medium', 'Strong']

for i in range(200):
    score = random.randint(10, 100)
    strength = (
        'Weak' if score < 40 else
        'Medium' if score < 70 else
        'Strong'
    )
    timestamp = datetime.utcnow() - timedelta(hours=random.randint(0, 240))

    password_data.append({
        "id": i + 1,
        "masked_password": "pa**rd" + str(i),
        "score": score,
        "strength": strength,
        "timestamp": timestamp
    })

df_password = pd.DataFrame(password_data)

# ----- Project Usage -----
projects = ['Calculator', 'Password Strength', 'Todo List', 'Notes', 'Stopwatch', 'Quotes']

project_data = []

for p in projects:
    project_data.append({
        "project": p,
        "views": random.randint(20, 150),
        "last_accessed": datetime.utcnow() - timedelta(days=random.randint(0, 10))
    })

df_projects = pd.DataFrame(project_data)

# ----- Todo Tasks -----
todo_data = []

for i in range(150):
    todo_data.append({
        "id": i + 1,
        "task": "Task " + str(i),
        "completed": random.choice([True, False]),
        "created_at": datetime.utcnow() - timedelta(hours=random.randint(0, 200))
    })

df_todo = pd.DataFrame(todo_data)

# ----- Notes -----
note_data = []

for i in range(120):
    note_data.append({
        "id": i + 1,
        "content": "Note content " + str(i),
        "created_at": datetime.utcnow() - timedelta(hours=random.randint(0, 200))
    })

df_notes = pd.DataFrame(note_data)

# ----- Calculator Logs -----
calc_data = []

ops = ["+", "-", "*", "/"]

for i in range(180):
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    expr = f"{a}{random.choice(ops)}{b}"

    calc_data.append({
        "id": i + 1,
        "expression": expr,
        "result": eval(expr),
        "created_at": datetime.utcnow() - timedelta(hours=random.randint(0, 200))
    })

df_calc = pd.DataFrame(calc_data)

# ====================================================
# 2. SAVE CLEAN CSV FILES (useful for Power BI/Excel)
# ====================================================
df_password.to_csv("password_analysis.csv", index=False)
df_projects.to_csv("project_usage.csv", index=False)
df_todo.to_csv("todo_data.csv", index=False)
df_notes.to_csv("notes_data.csv", index=False)
df_calc.to_csv("calculator_data.csv", index=False)

print("CSV files saved successfully.")

# ================================
# 3. ANALYSIS & INSIGHTS
# ================================

print("\n===== PASSWORD ANALYSIS =====")
print(df_password['strength'].value_counts())
print("\nAverage Score:", df_password['score'].mean())

# Trend chart
df_password = df_password.sort_values("timestamp")
df_password['date'] = df_password['timestamp'].dt.date

plt.figure()
df_password.groupby("date")['score'].mean().plot()
plt.title("Average Password Score Over Time")
plt.xlabel("Date")
plt.ylabel("Average Score")
plt.show()

# ================================
print("\n===== PROJECT USAGE =====")
print(df_projects.sort_values("views", ascending=False))

plt.figure()
plt.bar(df_projects['project'], df_projects['views'])
plt.xticks(rotation=45)
plt.title("Project Views")
plt.xlabel("Project")
plt.ylabel("Views")
plt.show()

# ================================
print("\n===== TODO ANALYSIS =====")
completed_rate = df_todo['completed'].mean() * 100
print(f"Task Completion Rate: {completed_rate:.2f}%")

df_todo['date'] = df_todo['created_at'].dt.date
tasks_per_day = df_todo.groupby("date")['id'].count()

plt.figure()
tasks_per_day.plot()
plt.title("Tasks Created Per Day")
plt.xlabel("Date")
plt.ylabel("Tasks")
plt.show()

# ================================
print("\n===== CALCULATOR USAGE =====")
df_calc['date'] = df_calc['created_at'].dt.date
calc_per_day = df_calc.groupby("date")['id'].count()
print(calc_per_day)

plt.figure()
calc_per_day.plot()
plt.title("Calculator Usage Per Day")
plt.xlabel("Date")
plt.ylabel("Count")
plt.show()

# ================================
print("\n===== NOTES ANALYSIS =====")
df_notes['date'] = df_notes['created_at'].dt.date
notes_per_day = df_notes.groupby("date")['id'].count()

plt.figure()
notes_per_day.plot()
plt.title("Notes Created Per Day")
plt.xlabel("Date")
plt.ylabel("Count")
plt.show()

print("\nAnalysis complete.")
