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
        
        self.label_timer = ttk.Label(timer_frame, text="00:00:00", font=("Helvetica", 20))
        self.label_timer.pack()
        
        self.button_start = ttk.Button(timer_frame, text="Start", command=self.start_timer)
        self.button_start.pack(side="left", padx=5)
        
        self.button_stop = ttk.Button(timer_frame, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.button_stop.pack(side="left", padx=5)
        
        # Initialize variables
        self.running_task = None
        self.start_time = None
        self.timer_id = None
        
    def create_task(self):
        title = self.entry_title.get()
        description = self.entry_description.get()
        priority = int(self.spinbox_priority.get())
        progress = 0
        time_spent = 0
        
        if title:
            self.cursor.execute("INSERT INTO tasks (title, description, priority, progress, time_spent) VALUES (?, ?, ?, ?, ?)",
                                (title, description, priority, progress, time_spent))
            self.connection.commit()
            self.display_tasks()
            
            self.entry_title.delete(0, tk.END)
            self.entry_description.delete(0, tk.END)
            self.spinbox_priority.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter a title for the task.")
            
    def display_tasks(self):
        self.tree_tasks.delete(*self.tree_tasks.get_children())
        
        self.cursor.execute("SELECT * FROM tasks")
        tasks = self.cursor.fetchall()
        
        for task in tasks:
            task_id, title, description, priority, progress, time_spent = task
            self.tree_tasks.insert("", "end", text=task_id, values=(title, description, priority, progress, time_spent))
    
    def delete_task(self):
        selected_item = self.tree_tasks.selection()
        
        if selected_item:
            task_id = int(self.tree_tasks.item(selected_item, "text"))
            
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this task?")
            
            if confirm:
                self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
                self.connection.commit()
                self.display_tasks()
        else:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            
    def update_task(self):
        selected_item = self.tree_tasks.selection()
        
        if selected_item:
            task_id = int(self.tree_tasks.item(selected_item, "text"))
            title = self.tree_tasks.item(selected_item, "values")[0]
            description = self.tree_tasks.item(selected_item, "values")[1]
            priority = int(self.tree_tasks.item(selected_item, "values")[2])
            progress = int(self.tree_tasks.item(selected_item, "values")[3])
            time_spent = int(self.tree_tasks.item(selected_item, "values")[4])
            
            dialog = UpdateTaskDialog(self, task_id, title, description, priority, progress, time_spent)
            self.wait_window(dialog)
            
            self.display_tasks()
        else:
            messagebox.showwarning("Warning", "Please select a task to update.")
            
    def show_progress(self):
        selected_item = self.tree_tasks.selection()
        
        if selected_item:
            task_id = int(self.tree_tasks.item(selected_item, "text"))
            progress = int(self.tree_tasks.item(selected_item, "values")[3])
            
            messagebox.showinfo("Progress", f"The progress of Task {task_id} is {progress}%.")
        else:
            messagebox.showwarning("Warning", "Please select a task to view progress.")
    
    def start_timer(self):
        selected_item = self.tree_tasks.selection()
        
        if selected_item:
            task_id = int(self.tree_tasks.item(selected_item, "text"))
            time_spent = int(self.tree_tasks.item(selected_item, "values")[4])
            
            self.running_task = task_id
            self.start_time = time.time() - time_spent
            self.update_timer()
            
            self.button_start.config(state=tk.DISABLED)
            self.button_stop.config(state=tk.NORMAL)
        else:
            messagebox.showwarning("Warning", "Please select a task to start the timer.")
            
    def stop_timer(self):
        self.running_task = None
        self.start_time = None
        self.label_timer.config(text="00:00:00")
        
        self.button_start.config(state=tk.NORMAL)
        self.button_stop.config(state=tk.DISABLED)
        
    def update_timer(self):
        if self.running_task and self.start_time:
            current_time = int(time.time() - self.start_time)
            hours = current_time // 3600
            minutes = (current_time % 3600) // 60
            seconds = current_time % 60
            
            time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.label_timer.config(text=time_string)
            
            self.cursor.execute("UPDATE tasks SET time_spent=? WHERE id=?", (current_time, self.running_task))
            self.connection.commit()
        
        self.timer_id = self.after(1000, self.update_timer)
        
        
class UpdateTaskDialog(tk.Toplevel):
    def __init__(self, parent, task_id, title, description, priority, progress, time_spent):
        super().__init__(parent)
        self.title("Update Task")
        self.transient(parent)
        
        self.parent = parent
        self.task_id = task_id
        
        self.label_title = ttk.Label(self, text="Title:")
        self.label_title.grid(row=0, column=0, sticky="E")
        self.entry_title = ttk.Entry(self, width=30)
        self.entry_title.grid(row=0, column=1, padx=10)
        self.entry_title.insert(0, title)
        
        self.label_description = ttk.Label(self, text="Description:")
        self.label_description.grid(row=1, column=0, sticky="E")
        self.entry_description = ttk.Entry(self, width=30)
        self.entry_description.grid(row=1, column=1, padx=10)
        self.entry_description.insert(0, description)
        
        self.label_priority = ttk.Label(self, text="Priority:")
        self.label_priority.grid(row=2, column=0, sticky="E")
        self.spinbox_priority = ttk.Spinbox(self, from_=1, to=10, width=5)
        self.spinbox_priority.grid(row=2, column=1, padx=10)
        self.spinbox_priority.delete(0, tk.END)
        self.spinbox_priority.insert(0, priority)
        
        self.label_progress = ttk.Label(self, text="Progress:")
        self.label_progress.grid(row=3, column=0, sticky="E")
        self.spinbox_progress = ttk.Spinbox(self, from_=0, to=100, width=5)
        self.spinbox_progress.grid(row=3, column=1, padx=10)
        self.spinbox_progress.delete(0, tk.END)
        self.spinbox_progress.insert(0, progress)
        
        self.button_update = ttk.Button(self, text="Update", command=self.update_task)
        self.button_update.grid(row=4, columnspan=2, pady=10)
        
    def update_task(self):
        title = self.entry_title.get()
        description = self.entry_description.get()
        priority = int(self.spinbox_priority.get())
        progress = int(self.spinbox_progress.get())
        
        self.parent.cursor.execute("UPDATE tasks SET title=?, description=?, priority=?, progress=? WHERE id=?",
                                   (title, description, priority, progress, self.task_id))
        self.parent.connection.commit()
        
        self.parent.display_tasks()
        self.destroy()

if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
