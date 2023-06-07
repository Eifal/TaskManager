import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import sqlite3
import time
import ttkthemes

# Initialize the application and database
app = tk.Tk()
app.title("Task Management Application")
connection = sqlite3.connect("task_manager.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, description TEXT, priority INTEGER, progress INTEGER, time_spent INTEGER)")
connection.commit()

# Application functions
def create_task():
    # Function to create a new task
    title = entry_title.get()
    description = entry_description.get()
    priority = spinbox_priority.get()
    progress = 0
    time_spent = 0

    cursor.execute("INSERT INTO tasks (title, description, priority, progress, time_spent) VALUES (?, ?, ?, ?, ?)",
                   (title, description, priority, progress, time_spent))
    connection.commit()

    messagebox.showinfo("Success", "Task successfully added")
    clear_fields()
    display_tasks()

def delete_task():
    # Function to delete a task
    selected_task = tree_tasks.selection()
    if not selected_task:
        messagebox.showwarning("Warning", "Select a task to delete")
        return

    confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this task?")
    if confirmation:
        task_id = tree_tasks.item(selected_task, "text")
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        connection.commit()
        messagebox.showinfo("Success", "Task successfully deleted")
        display_tasks()

def update_task():
    # Function to update a task
    selected_task = tree_tasks.selection()
    if not selected_task:
        messagebox.showwarning("Warning", "Select a task to update")
        return

    task_id = tree_tasks.item(selected_task, "text")
    title = entry_title.get()
    description = entry_description.get()
    priority = spinbox_priority.get()

    cursor.execute("UPDATE tasks SET title=?, description=?, priority=? WHERE id=?",
                   (title, description, priority, task_id))
    connection.commit()
    messagebox.showinfo("Success", "Task successfully updated")
    display_tasks()

def start_timer():
    # Function to start the timer
    global start_time, running_task
    selected_task = tree_tasks.selection()
    if not selected_task:
        messagebox.showwarning("Warning", "Select a task to start")
        return

    running_task = tree_tasks.item(selected_task, "text")
    start_time = time.time()
    button_start.config(state=tk.DISABLED)
    button_pause.config(state=tk.NORMAL)
    button_stop.config(state=tk.NORMAL)

def pause_timer():
    # Function to pause the timer
    global pause_time
    pause_time = time.time()
    button_start.config(state=tk.NORMAL)
    button_pause.config(state=tk.DISABLED)

def stop_timer():
    # Function to stop the timer
    global running_task, start_time
    elapsed_time = int(time.time() - start_time)
    cursor.execute("UPDATE tasks SET time_spent=time_spent + ? WHERE id=?", (elapsed_time, running_task))
    connection.commit()
    messagebox.showinfo("Success", "Timer stopped")
    button_start.config(state=tk.NORMAL)
    button_pause.config(state=tk.DISABLED)
    button_stop.config(state=tk.DISABLED)
    display_tasks()

def show_progress():
    # Function to display the progress of a task
    selected_task = tree_tasks.selection()
    if not selected_task:
        messagebox.showwarning("Warning", "Select a task to view progress")
        return

    task_id = tree_tasks.item(selected_task, "text")
    cursor.execute("SELECT progress FROM tasks WHERE id=?", (task_id,))
    progress = cursor.fetchone()[0]

    messagebox.showinfo("Task Progress", f"Task Progress: {progress}%")

def display_tasks():
    # Function to display the list of tasks
    tree_tasks.delete(*tree_tasks.get_children())
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    for task in tasks:
        tree_tasks.insert("", "end", text=task[0], values=(task[1], task[2], task[3], task[4], task[5]))

def clear_fields():
    # Function to clear the input fields
    entry_title.delete(0, tk.END)
    entry_description.delete(0, tk.END)
    spinbox_priority.delete(0, tk.END)
    spinbox_priority.insert(0, "1")

# Apply the themed style
style = ttkthemes.ThemedStyle(app)
style.set_theme("arc")  # Set the desired theme

# Create the application layout
frame_input = ttk.Frame(app)
frame_input.pack(pady=10)

label_title = ttk.Label(frame_input, text="Title:")
label_title.grid(row=0, column=0, sticky="E")

entry_title = ttk.Entry(frame_input, width=30)
entry_title.grid(row=0, column=1, padx=10)

label_description = ttk.Label(frame_input, text="Description:")
label_description.grid(row=1, column=0, sticky="E")

entry_description = ttk.Entry(frame_input, width=30)
entry_description.grid(row=1, column=1, padx=10)

label_priority = ttk.Label(frame_input, text="Priority:")
label_priority.grid(row=2, column=0, sticky="E")

spinbox_priority = ttk.Spinbox(frame_input, from_=1, to=10, width=5)
spinbox_priority.grid(row=2, column=1, padx=10)

button_create = ttk.Button(frame_input, text="Add Task", command=create_task)
button_create.grid(row=3, columnspan=2, pady=10)

frame_tasks = ttk.Frame(app)
frame_tasks.pack(pady=10)

tree_tasks = ttk.Treeview(frame_tasks, columns=("Title", "Description", "Priority", "Progress", "Time Spent"))
tree_tasks.heading("#0", text="ID")
tree_tasks.heading("Title", text="Title")
tree_tasks.heading("Description", text="Description")
tree_tasks.heading("Priority", text="Priority")
tree_tasks.heading("Progress", text="Progress")
tree_tasks.heading("Time Spent", text="Time Spent")
tree_tasks.column("#0", width=30)
tree_tasks.column("Title", width=100)
tree_tasks.column("Description", width=150)
tree_tasks.column("Priority", width=70)
tree_tasks.column("Progress", width=70)
tree_tasks.column("Time Spent", width=100)
tree_tasks.pack()

frame_buttons = ttk.Frame(app)
frame_buttons.pack(pady=10)

button_delete = ttk.Button(frame_buttons, text="Delete Task", command=delete_task)
button_delete.grid(row=0, column=0, padx=5)

button_update = ttk.Button(frame_buttons, text="Update Task", command=update_task)
button_update.grid(row=0, column=1, padx=5)

button_progress = ttk.Button(frame_buttons, text="View Progress", command=show_progress)
button_progress.grid(row=0, column=2, padx=5)

frame_timer = ttk.Frame(app)
frame_timer.pack(pady=10)

button_start = ttk.Button(frame_timer, text="Start", command=start_timer)
button_start.grid(row=0, column=0, padx=5)

button_pause = ttk.Button(frame_timer, text="Pause", state=tk.DISABLED, command=pause_timer)
button_pause.grid(row=0, column=1, padx=5)

button_stop = ttk.Button(frame_timer, text="Stop", state=tk.DISABLED, command=stop_timer)
button_stop.grid(row=0, column=2, padx=5)

# Run the application
display_tasks()
app.mainloop()
