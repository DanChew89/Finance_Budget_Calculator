import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from fpdf import FPDF

# Main application class
class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget App")

        # Scrollable canvas and frame setup
        self.canvas = tk.Canvas(root)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Packing canvas and scrollbar
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        # Configure frame resizing and scrolling
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # List to hold all header objects
        self.headers = []

        # Button to add a new header
        self.add_header_button = tk.Button(root, text="Add Header", command=self.add_header)
        self.add_header_button.pack(pady=5)

        # Button to export data to PDF
        self.export_button = tk.Button(root, text="Export to PDF", command=self.export_to_pdf)
        self.export_button.pack(pady=5)

    def add_header(self):
        header_frame = HeaderFrame(self.scroll_frame, self.update_canvas_scroll, self.remove_header)
        self.headers.append(header_frame)
        header_frame.pack(pady=10, fill='x')

    def update_canvas_scroll(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def remove_header(self, header_frame):
        # Remove the header from the list and destroy it from the UI
        self.headers.remove(header_frame)
        header_frame.destroy()
        self.update_canvas_scroll()

    def export_to_pdf(self):
        if not self.headers:
            messagebox.showwarning("Warning", "No data to export!")
            return

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for header in self.headers:
            header_name = header.header_name_var.get().strip()
            if not header_name:
                continue  # Skip headers without a name

            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt=header_name, ln=True, align='L')
            pdf.set_font("Arial", size=12)

            total = 0
            entries_exist = False

            for desc, amount in header.entries:
                desc_text = desc.get().strip()
                amount_text = amount.get().strip()
                if desc_text and amount_text:
                    try:
                        amount_value = float(amount_text)
                        entries_exist = True
                        pdf.cell(100, 10, txt=f"Description: {desc_text}", border=0)
                        pdf.cell(40, 10, txt=f"Amount: ${amount_value:.2f}", ln=True)
                        total += amount_value
                    except ValueError:
                        continue

            if entries_exist:
                pdf.cell(40, 10, txt=f"Total: ${total:.2f}", ln=True, align='R')
                pdf.ln(5)

        pdf_file = "budget_report.pdf"
        pdf.output(pdf_file)
        messagebox.showinfo("Export Complete", f"Data exported to {pdf_file}")

class HeaderFrame(tk.Frame):
    def __init__(self, parent, update_scroll_callback, remove_header_callback):
        super().__init__(parent, bd=2, relief='ridge')
        self.entries = []
        self.update_scroll_callback = update_scroll_callback
        self.remove_header_callback = remove_header_callback

        # Header name entry
        self.header_name_var = tk.StringVar(value="New Header")
        self.header_name_entry = tk.Entry(self, textvariable=self.header_name_var, font=("Arial", 14))
        self.header_name_entry.pack(padx=5, pady=5)

        # Remove header button
        self.remove_header_button = tk.Button(self, text="Remove Header", command=self.remove_self)
        self.remove_header_button.pack(pady=5)

        # Frame for entries with scrollbar
        self.entries_frame = ttk.Frame(self)
        self.entries_frame.pack(padx=5, pady=5, fill='x')

        # Button to add an entry
        self.add_entry_button = tk.Button(self, text="Add Entry", command=self.add_entry)
        self.add_entry_button.pack(pady=5)

        # Label to show total
        self.total_label = tk.Label(self, text="Total: $0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=5)

    def add_entry(self):
        entry_frame = EntryFrame(self.entries_frame, self.update_total)
        self.entries.append((entry_frame.description_var, entry_frame.amount_var))
        entry_frame.pack(pady=2, fill='x')
        self.update_scroll_callback()

    def update_total(self):
        total = 0
        for desc, amount in self.entries:
            try:
                total += float(amount.get())
            except ValueError:
                pass
        self.total_label.config(text=f"Total: ${total:.2f}")

    def remove_entry(self, entry_frame):
        # Remove the entry from the list and update the total
        self.entries.remove((entry_frame.description_var, entry_frame.amount_var))
        entry_frame.destroy()
        self.update_total()

    def remove_self(self):
        # Call the callback to remove this header from the parent list and UI
        self.remove_header_callback(self)

class EntryFrame(tk.Frame):
    def __init__(self, parent, update_callback):
        super().__init__(parent)
        self.update_callback = update_callback

        # Entry for description
        self.description_var = tk.StringVar()
        self.description_entry = tk.Entry(self, textvariable=self.description_var, width=30)
        self.description_entry.grid(row=0, column=0, padx=5, pady=2)

        # Entry for amount
        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(self, textvariable=self.amount_var, width=10)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=2)

        # Button to remove this entry
        self.remove_button = tk.Button(self, text="Remove", command=self.remove_entry)
        self.remove_button.grid(row=0, column=2, padx=5, pady=2)

        # Bind variable change to the update callback
        self.amount_var.trace_add("write", lambda *args: self.update_callback())

    def remove_entry(self):
        # Call parent to remove the entry from the entries list and update total
        self.master.master.remove_entry(self)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")  # Set a reasonable starting size for the window
    app = BudgetApp(root)
    root.mainloop()
