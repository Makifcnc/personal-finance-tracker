import pandas as pd
import csv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data_entry import get_amount, get_category, get_date, get_description


class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        messagebox.showinfo("Success", "Entry added successfully")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            messagebox.showinfo(
                "No Transactions", "No transactions found in the given date range."
            )
        else:
            messagebox.showinfo(
                "Transactions",
                f"Transactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}",
            )
        return filtered_df


def add():
    CSV.initialize_csv()
    date = get_date(
        "Enter the date of the transaction (dd-mm-yyyy) or enter for today's date: ",
        allow_default=True,
    )
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)


def plot_transactions(df, root):
    df.set_index("date", inplace=True)
    income_df = (
        df[df["category"] == "Income"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )
    expense_df = (
        df[df["category"] == "Expense"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(income_df.index, income_df["amount"], label="Income", color="g")
    ax.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount")
    ax.set_title("Income and Expense Over Time")
    ax.legend()
    ax.grid(True)

    top = tk.Toplevel(root)
    top.title("Transaction Plot")
    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack()


def main():
    root = tk.Tk()
    root.title("Finance Tracker")
    root.geometry("500x300")

    ttk.Button(root, text="Add Transaction", command=add).pack()

    def view_transactions():
        start_date = get_date("Enter the start date (dd-mm-yyyy): ")
        end_date = get_date("Enter the end date (dd-mm-yyyy): ")
        df = CSV.get_transactions(start_date, end_date)
        if not df.empty and messagebox.askyesno("Plot", "Do you want to see a plot?"):
            plot_transactions(df, root)

    ttk.Button(root, text="View Transactions", command=view_transactions).pack()
    ttk.Button(root, text="Exit", command=root.quit).pack()

    root.mainloop()


if __name__ == "__main__":
    main()
