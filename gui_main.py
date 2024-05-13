import tkinter as tk
from tkinter import ttk

PADDING = 16

root = tk.Tk()

# Set the title
root.title("Processes")

# Maximize the window size
# root.state("zoomed")

# Create a frame for the search bar with padding
search_frame = tk.Frame(root, padx=PADDING, pady=PADDING)
search_frame.grid(row=0, column=0, sticky="ew")
search_frame.pack(side=tk.TOP, fill=tk.X)

# Add a label for the search bar
search_label = tk.Label(search_frame, text="Search")
search_label.pack(side=tk.LEFT)

# Add an entry widget for the search bar
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, expand=False, fill=tk.X)

search_frame.place(relx=0.5, rely=0.0, anchor=tk.N)

# Create a Treeview widget
tree = ttk.Treeview(root, columns=("Name", "Age", "Gender"))

# Define columns
tree.heading("#0", text="ID")
tree.heading("Name", text="Name")
tree.heading("Age", text="Age")
tree.heading("Gender", text="Gender")
tree.grid(row=1, column=0, sticky="nsew")

# Inserting some sample data into the Treeview
for i in range(1, 11):
    tree.insert("", tk.END, text=f"Item {i}", values=(f"Name {i}", f"{20+i}", f'{"Male" if i % 2 == 0 else "Female"}'))

# Pack the Treeview widget
tree.pack(expand=True, fill="both")

# Configure grid to expand properly
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
