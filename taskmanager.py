import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import time

class TaskManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Management Application")
        
        # Connect to the database
        self.connection = sqlite3.connect("task_manager.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, description TEXT, priority INTEGER, progress INTEGER, time_spent INTEGER)")
        self.connection.commit()
        
        # Create and configure widgets
        self.create_widgets()
        self.display_tasks()
        
    def create_widgets(self):
        # Create input frame
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)
        
        label_title = ttk.Label(input_frame, text="Title:")
        label_title.grid(row=0, column=0, sticky="E")
        self.entry_title = ttk.Entry(input_frame, width=30)
        self.entry_title.grid(row=0, column=1, padx=10)
        
        label_description = ttk.Label(input_frame, text="Description:")
        label_description.grid(row=1, column=0, sticky="E")
        self.entry_description = ttk.Entry(input_frame, width=30)
        self.entry_description.grid(row=1, column=1, padx=10)
        
        label_priority = ttk.Label(input_frame, text="Priority:")
        label_priority.grid(row=2, column=0, sticky="E")
        self.spinbox_priority = ttk.Spinbox(input_frame, from_=1, to=10, width=5)
        self.spinbox_priority.grid(row=2, column=1, padx=10)
        
        button_create = ttk.Button(input_frame, text="Add Task", command=self.create_task)
        button_create.grid(row=3, columnspan=2, pady=10)
        
        # Create tasks treeview
        self.tree_tasks = ttk.Treeview(self, columns=("Title", "Description", "Priority", "Progress", "Time Spent"))
        self.tree_tasks.heading("#0", text="ID")
        self.tree_tasks.heading("Title", text="Title")
        self.tree_tasks.heading("Description", text="Description")
        self.tree_tasks.heading("Priority", text="Priority")
        self.tree_tasks.heading("Progress", text="Progress")
        self.tree_tasks.heading("Time Spent", text="Time Spent")
        self.tree_tasks.column("#0", width=30)
        self.tree_tasks.column("Title", width=100)
        self.tree_tasks.column("Description", width=150)
        self.tree_tasks.column("Priority", width=70)
        self.tree_tasks.column("Progress", width=70)
        self.tree_tasks.column("Time Spent", width=100)
        self.tree_tasks.pack()
        
        # Create buttons frame
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(pady=10)
        
        button_delete = ttk.Button(buttons_frame, text="Delete Task", command=self.delete_task)
        button_delete.pack(side="left", padx=5)
        
        button_update = ttk.Button(buttons_frame, text="Update Task", command=self.update_task)
        button_update.pack(side="left", padx=5)
        
        button_progress = ttk.Button(buttons_frame, text="View Progress", command=self.show_progress)
        button_progress.pack(side="left", padx=5)
        
        # Create timer frame
        timer_frame = ttk.Frame(self)
        timer_frame.pack(pady=10)
        
        button_start = ttk.Button(timer_frame, text="Start", command=self.start_timer)
        button_start.pack(side="left", padx=5)
        
        button_pause = ttk.Button(timer_frame, text="Pause", state=tk.DISABLED, command=self.pause_timer)
        button_pause.pack(side="left", padx=5)
        
        button_stop = ttk.Button(timer_frame, text="Stop", state=tk.DISABLED, command=self.stop_timer)
        button_stop.pack(side="left", padx=5)
        
    def create_task(self):
        # Create a new task
        title = self.entry_title.get()
        description = self.entry_description.get()
        priority = int(self.spinbox_priority.get())
        progress = 0
        time_spent = 0

        self.cursor.execute("INSERT INTO tasks (title, description, priority, progress, time_spent) VALUES (?, ?, ?, ?, ?)",
                           (title, description, priority, progress, time_spent))
        self.connection.commit()

        messagebox.showinfo("Success", "Task successfully added")
        self.clear_fields()
        self.display_tasks()
        
    def delete_task(self):
        # Delete a task
        selected_task = self.tree_tasks.selection()
        if not selected_task:
            messagebox.showwarning("Warning", "Select a task to delete")
            return

        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this task?")
        if confirmation:
            task_id = self.tree_tasks.item(selected_task, "text")
            self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.connection.commit()
            messagebox.showinfo("Success", "Task successfully deleted")
            self.display_tasks()
            
    def update_task(self):
        # Update a task
        selected_task = self.tree_tasks.selection()
        if not selected_task:
            messagebox.showwarning("Warning", "Select a task to update")
            return

        task_id = self.tree_tasks.item(selected_task, "text")
        title = self.entry_title.get()
        description = self.entry_description.get()
        priority = int(self.spinbox_priority.get())

        self.cursor.execute("UPDATE tasks SET title=?, description=?, priority=? WHERE id=?",
                           (title, description, priority, task_id))
        self.connection.commit()
        messagebox.showinfo("Success", "Task successfully updated")
        self.display_tasks()
        
    def start_timer(self):
        # Start the timer
        selected_task = self.tree_tasks.selection()
        if not selected_task:
            messagebox.showwarning("Warning", "Select a task to start")
            return

        self.running_task = self.tree_tasks.item(selected_task, "text")
        self.start_time = time.time()
        self.button_start.config(state=tk.DISABLED)
        self.button_pause.config(state=tk.NORMAL)
        self.button_stop.config(state=tk.NORMAL)
        
    def pause_timer(self):
        # Pause the timer
        self.pause_time = time.time()
        self.button_start.config(state=tk.NORMAL)
        self.button_pause.config(state=tk.DISABLED)
        
    def stop_timer(self):
        # Stop the timer
        elapsed_time = int(time.time() - self.start_time)
        self.cursor.execute("UPDATE tasks SET time_spent=time_spent + ? WHERE id=?", (elapsed_time, self.running_task))
        self.connection.commit()
        messagebox.showinfo("Success", "Timer stopped")
        self.button_start.config(state=tk.NORMAL)
        self.button_pause.config(state=tk.DISABLED)
        self.button_stop.config(state=tk.DISABLED)
        self.display_tasks()
        
    def show_progress(self):
        # Display the progress of a task
        selected_task = self.tree_tasks.selection()
        if not selected_task:
            messagebox.showwarning("Warning", "Select a task to view progress")
            return

        task_id = self.tree_tasks.item(selected_task, "text")
        self.cursor.execute("SELECT progress FROM tasks WHERE id=?", (task_id,))
        progress = self.cursor.fetchone()[0]

        messagebox.showinfo("Task Progress", f"Task Progress: {progress}%")
        
    def display_tasks(self):
        # Display the list of tasks
        self.tree_tasks.delete(*self.tree_tasks.get_children())
        self.cursor.execute("SELECT * FROM tasks")
        tasks = self.cursor.fetchall()
        for task in tasks:
            self.tree_tasks.insert("", "end", text=task[0], values=(task[1], task[2], task[3], task[4], task[5]))
            
    def clear_fields(self):
        # Clear the input fields
        self.entry_title.delete(0, tk.END)
        self.entry_description.delete(0, tk.END)
        self.spinbox_priority.delete(0, tk.END)
        self.spinbox_priority.insert(0, "1")
        
    def on_closing(self):
        # Close the application and disconnect from the database
        self.connection.close()
        self.destroy()

if __name__ == "__main__":
    app = TaskManagerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
