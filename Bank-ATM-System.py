import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import mysql.connector
from datetime import datetime
from decimal import Decimal

# Transaction Class
class Transaction:
    def __init__(self, transaction_id, account_number, amount, transaction_type, date):
        self.transaction_id = transaction_id
        self.account_number = account_number
        self.amount = amount
        self.transaction_type = transaction_type
        self.date = date

    def save_to_db(self, db_connection):
        try:
            cursor = db_connection.cursor()
            query = """
                INSERT INTO transactions (account_number, amount, transaction_type, date)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (self.account_number, str(self.amount), self.transaction_type, self.date))
            db_connection.commit()
            self.transaction_id = cursor.lastrowid
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error saving transaction: {err}")

# Account Class
class Account:
    def __init__(self, account_number, account_holder, profession, address, phone_number, balance):
        self.account_number = account_number
        self.account_holder = account_holder
        self.profession = profession
        self.address = address
        self.phone_number = phone_number
        self.balance = Decimal(balance)
        self.transactions = []

    def update_balance_in_db(self, db_connection):
        try:
            cursor = db_connection.cursor()
            query = "UPDATE accounts SET balance = %s WHERE account_number = %s"
            cursor.execute(query, (str(self.balance), self.account_number))
            db_connection.commit()
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating balance: {err}")

    def load_transactions(self, db_connection):
        self.transactions = []
        try:
            cursor = db_connection.cursor()
            query = """
                SELECT id, account_number, amount, transaction_type, date
                FROM transactions WHERE account_number = %s
            """
            cursor.execute(query, (self.account_number,))
            for row in cursor.fetchall():
                transaction = Transaction(
                    transaction_id=row[0],
                    account_number=row[1],
                    amount=row[2],
                    transaction_type=row[3],
                    date=row[4]
                )
                self.transactions.append(transaction)
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading transactions: {err}")

# ATM Application
class ATMApp:
    def __init__(self, root, db_connection):
        self.root = root
        self.db_connection = db_connection
        self.current_account = None

        self.root.title("ATM System")
        self.root.geometry("400x500")
        self.root.resizable(True, True)

        self.create_login_frame()

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.login_frame, text="Account Number:").grid(row=0, column=0, pady=10, sticky="w")
        self.account_entry = tk.Entry(self.login_frame)
        self.account_entry.grid(row=0, column=1, pady=10)

        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0, pady=10, sticky="w")
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=10)

        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, columnspan=2, pady=20)
        ttk.Button(self.login_frame, text="Change Password", command=self.change_password_prompt).grid(row=3, columnspan=2, pady=10)

    def login(self):
        account_number = self.account_entry.get()
        password = self.password_entry.get()
        cursor = self.db_connection.cursor()
        query = "SELECT account_number, account_holder, profession, address, phone_number, balance FROM accounts WHERE account_number = %s AND password = %s"
        cursor.execute(query, (account_number, password))
        result = cursor.fetchone()
        cursor.close()

        if result:
            self.current_account = Account(
                account_number=result[0],
                account_holder=result[1],
                profession=result[2],
                address=result[3],
                phone_number=result[4],
                balance=result[5]
            )
            self.current_account.load_transactions(self.db_connection)
            self.login_frame.pack_forget()
            self.create_main_menu()
            messagebox.showinfo("Login Successful", f"Welcome, {self.current_account.account_holder}!")
        else:
            messagebox.showerror("Error", "Invalid account number or password.")

    def change_password_prompt(self):
        account_number = simpledialog.askstring("Change Password", "Enter your account number:")
        current_password = simpledialog.askstring("Change Password", "Enter your current password:", show="*")

        cursor = self.db_connection.cursor()
        query = "SELECT account_number FROM accounts WHERE account_number = %s AND password = %s"
        cursor.execute(query, (account_number, current_password))
        result = cursor.fetchone()

        if result:
            new_password = simpledialog.askstring("Change Password", "Enter your new password:", show="*")
            confirm_password = simpledialog.askstring("Change Password", "Confirm your new password:", show="*")

            if new_password == confirm_password:
                update_query = "UPDATE accounts SET password = %s WHERE account_number = %s"
                cursor.execute(update_query, (new_password, account_number))
                self.db_connection.commit()
                messagebox.showinfo("Success", "Password changed successfully.")
            else:
                messagebox.showerror("Error", "Passwords do not match.")
        else:
            messagebox.showerror("Error", "Invalid account number or current password.")
        cursor.close()

    def create_main_menu(self):
        self.main_menu_frame = tk.Frame(self.root)
        self.main_menu_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.main_menu_frame, text=f"Welcome, {self.current_account.account_holder}").pack(pady=10)
        ttk.Button(self.main_menu_frame, text="View Balance", command=self.view_balance).pack(pady=10)
        ttk.Button(self.main_menu_frame, text="Deposit", command=self.deposit_prompt).pack(pady=10)
        ttk.Button(self.main_menu_frame, text="Withdraw", command=self.withdraw_prompt).pack(pady=10)
        ttk.Button(self.main_menu_frame, text="Transfer Money", command=self.transfer_prompt).pack(pady=10)
        ttk.Button(self.main_menu_frame, text="View Transactions", command=self.view_transactions).pack(pady=10)
        ttk.Button(self.main_menu_frame, text="Logout", command=self.logout).pack(pady=10)

    def view_balance(self):
        messagebox.showinfo("Balance", f"Your balance is: {self.current_account.balance}")

    def deposit_prompt(self):
        amount = simpledialog.askfloat("Deposit", "Enter the amount to deposit:")
        if amount:
            self.current_account.balance += Decimal(amount)
            self.current_account.update_balance_in_db(self.db_connection)
            transaction = Transaction(None, self.current_account.account_number, amount, "Deposit", datetime.now())
            transaction.save_to_db(self.db_connection)
            messagebox.showinfo("Success", f"{amount} deposited successfully. New Balance: {self.current_account.balance}")

    def withdraw_prompt(self):
        amount = simpledialog.askfloat("Withdraw", "Enter the amount to withdraw:")
        if amount:
            if self.current_account.balance >= Decimal(amount):
                self.current_account.balance -= Decimal(amount)
                self.current_account.update_balance_in_db(self.db_connection)
                transaction = Transaction(None, self.current_account.account_number, amount, "Withdrawal", datetime.now())
                transaction.save_to_db(self.db_connection)
                messagebox.showinfo("Success", f"{amount} withdrawn successfully. New Balance: {self.current_account.balance}")
            else:
                messagebox.showerror("Error", "Insufficient balance.")

    def transfer_prompt(self):
        transfer_to_account = simpledialog.askstring("Transfer Money", "Enter the account number to transfer to:")
        transfer_amount = simpledialog.askfloat("Transfer Money", "Enter the amount to transfer:")

        if transfer_amount:
            if self.current_account.balance >= Decimal(transfer_amount):
                cursor = self.db_connection.cursor()
                
                # Check if the recipient account exists
                query = "SELECT account_number, balance FROM accounts WHERE account_number = %s"
                cursor.execute(query, (transfer_to_account,))
                result = cursor.fetchone()
                
                if result:
                    recipient_balance = result[1]  # Get recipient's balance

                    # Deduct from A's balance
                    self.current_account.balance -= Decimal(transfer_amount)
                    self.current_account.update_balance_in_db(self.db_connection)

                    # Add to B's balance
                    recipient_account = Account(account_number=result[0], account_holder="", profession="", address="", phone_number="", balance=recipient_balance)
                    recipient_account.balance += Decimal(transfer_amount)
                    recipient_account.update_balance_in_db(self.db_connection)

                    # Save transaction for A
                    transaction = Transaction(None, self.current_account.account_number, transfer_amount, "Transfer", datetime.now())
                    transaction.save_to_db(self.db_connection)

                    # Save transaction for B
                    transaction = Transaction(None, transfer_to_account, transfer_amount, "Transfer", datetime.now())
                    transaction.save_to_db(self.db_connection)

                    messagebox.showinfo("Success", f"{transfer_amount} transferred successfully to {transfer_to_account}. New Balance: {self.current_account.balance}")
                else:
                    messagebox.showerror("Error", "Invalid recipient account number.")
                
                cursor.close()
            else:
                messagebox.showerror("Error", "Insufficient balance.")

    def view_transactions(self):
        transaction_details = "\n".join([f"ID: {t.transaction_id}, Type: {t.transaction_type}, Amount: {t.amount}, Date: {t.date}" for t in self.current_account.transactions])
        messagebox.showinfo("Transactions", transaction_details if transaction_details else "No transactions found.")

    def logout(self):
        self.main_menu_frame.pack_forget()
        self.create_login_frame()

# Main Execution
if __name__ == "__main__":
    # Create a connection to the database
    db_connection = mysql.connector.connect(
        host="localhost", user="root", password="", database="bank"
    )

    root = tk.Tk()
    app = ATMApp(root, db_connection)
    root.mainloop()
