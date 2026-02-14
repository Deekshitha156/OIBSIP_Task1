import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

HISTORY_FILE = 'bmi_history.csv'
use_imperial = False


# Custom styling
def setup_style():
    style = ttk.Style()
    style.theme_use('clam')  # Modern theme

    # Configure styles
    style.configure('Title.TLabel', font=('Arial', 18, 'bold'), foreground='#2c3e50')
    style.configure('Result.TLabel', font=('Arial', 16, 'bold'), foreground='#27ae60')
    style.configure('Advice.TLabel', font=('Arial', 11), foreground='#34495e', wraplength=500)
    style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#2c3e50')

    style.configure('Accent.TButton', font=('Arial', 10, 'bold'), background='#3498db')
    style.configure('Danger.TButton', font=('Arial', 10, 'bold'), background='#e74c3c')
    style.configure('Success.TButton', font=('Arial', 10, 'bold'), background='#27ae60')

    style.map('Accent.TButton', background=[('active', '#2980b9')])
    style.map('Danger.TButton', background=[('active', '#c0392b')])
    style.map('Success.TButton', background=[('active', '#229954')])


def toggle_units():
    global use_imperial
    use_imperial = not use_imperial
    units_label.config(text="Imperial (inches/lb)" if use_imperial else "Metric (m/kg)")


def compute_bmi():
    try:
        if use_imperial:
            h = float(height_entry.get()) / 39.37
            w = float(weight_entry.get()) / 2.205
            unit_text = " (inches/lb)"
        else:
            h = float(height_entry.get())
            w = float(weight_entry.get())
            unit_text = " (m/kg)"

        if not (0.5 <= h <= 3 and 10 <= w <= 500):
            raise ValueError("Use realistic values: height 0.5-3m, weight 10-500kg")

        bmi = round(w / (h ** 2), 1)
        status = classify_bmi(bmi)
        result_label.config(text=f"BMI: {bmi}{unit_text} | {status}")
        show_advice(status)
        log_entry(h, w, bmi, status)
        refresh_history()
        draw_trend()
    except ValueError as err:
        messagebox.showwarning("Input Error", str(err))


def classify_bmi(bmi):
    if bmi < 18.5: return "Underweight"
    if bmi < 25: return "Normal weight"
    if bmi < 30: return "Overweight"
    return "Obese"


def show_advice(status):
    advice = {
        "Underweight": "Consider consulting a nutritionist for healthy weight gain strategies.",
        "Normal weight": "Excellent! Maintain balance with diet and regular exercise.",
        "Overweight": "Focus on portion control, daily walks, and healthy food choices.",
        "Obese": "Professional guidance recommended for sustainable weight management."
    }
    advice_label.config(text=advice.get(status, "Keep tracking your progress!"))


def log_entry(h, w, bmi, status):
    row = [datetime.now().strftime("%Y-%m-%d %H:%M"), f"{h:.2f}", f"{w:.1f}", bmi, status]
    with open(HISTORY_FILE, 'a', newline='') as f:
        csv.writer(f).writerow(row)


def refresh_history():
    tree.delete(*tree.get_children())
    try:
        with open(HISTORY_FILE, 'r') as f:
            for row in reversed(list(csv.reader(f))[-50:]):
                tree.insert('', 'end', values=row)
    except FileNotFoundError:
        pass


def delete_selected():
    sel = tree.selection()
    if sel:
        for item in sel:
            tree.delete(item)
        export_csv()
        messagebox.showinfo("Success", "Selected entries deleted.")
    else:
        messagebox.showinfo("Info", "Please select rows to delete.")


def export_csv():
    rows = [['Date', 'Height', 'Weight', 'BMI', 'Status']] + [tree.item(item)['values'] for item in tree.get_children()]
    with open(HISTORY_FILE, 'w', newline='') as f:
        csv.writer(f).writerows(rows)


def import_csv():
    file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file:
        with open(file, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            with open(HISTORY_FILE, 'a', newline='') as out:
                writer = csv.writer(out)
                writer.writerows(reader)
        refresh_history()
        draw_trend()
        messagebox.showinfo("Success", "Data imported successfully.")


def draw_trend():
    try:
        data = list(csv.reader(open(HISTORY_FILE)))
        if len(data) < 2: return
        dates = [row[0] for row in data[-20:]]
        bmis = [float(row[3]) for row in data[-20:]]

        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(range(len(bmis)), bmis, marker='o', linewidth=3, markersize=8,
                color='#3498db', markerfacecolor='#27ae60')
        ax.set_xlabel('Recent Entries (newest →)', fontsize=11, color='#2c3e50')
        ax.set_ylabel('BMI', fontsize=11, color='#2c3e50')
        ax.set_title('Your BMI Progress', fontsize=14, fontweight='bold', color='#2c3e50')
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#ecf0f1')
        canvas.draw()
    except:
        pass


# Main window with styling
root = tk.Tk()
root.title("🏥 Advanced BMI Calculator")
root.geometry("700x750")
root.configure(bg='#f8f9fa')

# Apply custom styles
setup_style()

# Header
header_frame = tk.Frame(root, bg='#3498db', height=80)
header_frame.pack(fill='x', pady=(0, 20))
header_frame.pack_propagate(False)

tk.Label(header_frame, text="BMI Tracker", font=('Arial', 24, 'bold'),
         fg='white', bg='#3498db').pack(expand=True)

# Units toggle
units_frame = tk.Frame(root, bg='#f8f9fa')
units_frame.pack(pady=10)
units_label = tk.Label(units_frame, text="Metric (m/kg)", font=('Arial', 11, 'bold'),
                       bg='#f8f9fa', fg='#2c3e50')
units_label.pack(side='left')
tk.Button(units_frame, text="🔄 Toggle Units", command=toggle_units,
          bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
          relief='flat', padx=20).pack(side='left', padx=10)

# Notebook with styled tabs
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))

# Input Tab
input_tab = ttk.Frame(notebook)
notebook.add(input_tab, text="📊 Calculate BMI")

# Input form with styling
form_frame = tk.Frame(input_tab, bg='#f8f9fa', relief='ridge', bd=2)
form_frame.pack(pady=30, padx=50, fill='x')

ttk.Label(form_frame, text="Height:", style='Header.TLabel').pack(pady=15)
height_entry = ttk.Entry(form_frame, font=('Arial', 12), width=15)
height_entry.pack(pady=5)

ttk.Label(form_frame, text="Weight:", style='Header.TLabel').pack(pady=(20, 15))
weight_entry = ttk.Entry(form_frame, font=('Arial', 12), width=15)
weight_entry.pack(pady=5)

btn_frame = tk.Frame(form_frame, bg='#f8f9fa')
btn_frame.pack(pady=25)

ttk.Button(btn_frame, text="🚀 Calculate BMI", command=compute_bmi, style='Accent.TButton').pack(side='left', padx=10)
ttk.Button(btn_frame, text="🗑️ Clear", command=lambda: [height_entry.delete(0, tk.END),
                                                        weight_entry.delete(0, tk.END), result_label.config(text=""),
                                                        advice_label.config(text="")], style='Danger.TButton').pack(
    side='left')

result_label = ttk.Label(input_tab, text="Enter values to calculate", style='Result.TLabel')
result_label.pack(pady=20)

advice_label = ttk.Label(input_tab, text="Your personalized advice will appear here", style='Advice.TLabel')
advice_label.pack(pady=10)

# History Tab
hist_tab = ttk.Frame(notebook)
notebook.add(hist_tab, text="📋 History")

tree_frame = tk.Frame(hist_tab, relief='sunken', bd=2, bg='#ecf0f1')
tree_frame.pack(fill='both', expand=True, padx=20, pady=20)

tree = ttk.Treeview(tree_frame, columns=('Date', 'Height', 'Weight', 'BMI', 'Status'),
                    show='headings', height=12, style='Treeview')
for col in tree['columns']:
    tree.heading(col, text=col)
    tree.column(col, width=100)

scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

hist_btn_frame = tk.Frame(hist_tab, bg='#f8f9fa')
hist_btn_frame.pack(pady=15)

ttk.Button(hist_btn_frame, text="🗑️ Delete Selected", command=delete_selected, style='Danger.TButton').pack(side='left',
                                                                                                            padx=10)
ttk.Button(hist_btn_frame, text="📤 Export CSV", command=export_csv, style='Success.TButton').pack(side='left', padx=10)
ttk.Button(hist_btn_frame, text="📥 Import CSV", command=import_csv, style='Accent.TButton').pack(side='left', padx=10)

# Graph Tab
graph_tab = ttk.Frame(notebook)
notebook.add(graph_tab, text="📈 Trends")

graph_frame = tk.Frame(graph_tab, bg='#f8f9fa', relief='ridge', bd=2)
graph_frame.pack(fill='both', expand=True, padx=20, pady=20)

fig, ax = plt.subplots(figsize=(10, 5), facecolor='#f8f9fa')
canvas = FigureCanvasTkAgg(fig, graph_frame)
canvas.get_tk_widget().pack(fill='both', expand=True)

# Initialize
refresh_history()
draw_trend()
root.mainloop()
