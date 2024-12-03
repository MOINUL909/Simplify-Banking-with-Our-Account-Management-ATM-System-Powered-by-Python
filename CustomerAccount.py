import mysql.connector
import bcrypt
from tkinter import Tk, Label, Entry, Button, Frame, messagebox


class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Account Data Entry")
        self.root.geometry("500x600")
        self.root.resizable(True, True)  # Allow resizing

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        self.main_frame = Frame(self.root, padx=20, pady=20)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid to make the layout responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Title
        Label(
            self.main_frame,
            text="Bank Account Entry",
            font=("Arial", 16, "bold"),
            fg="blue",
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="nsew")

        # Account Holder
        Label(self.main_frame, text="Account Holder:", font=("Arial", 12)).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.account_holder_entry = Entry(self.main_frame, font=("Arial", 12))
        self.account_holder_entry.grid(row=1, column=1, pady=5, sticky="nsew")

        # Address
        Label(self.main_frame, text="Address:", font=("Arial", 12)).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.address_entry = Entry(self.main_frame, font=("Arial", 12))
        self.address_entry.grid(row=2, column=1, pady=5, sticky="nsew")

        # Phone Number
        Label(self.main_frame, text="Phone Number:", font=("Arial", 12)).grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.phone_number_entry = Entry(self.main_frame, font=("Arial", 12))
        self.phone_number_entry.grid(row=3, column=1, pady=5, sticky="nsew")

        # Profession
        Label(self.main_frame, text="Profession:", font=("Arial", 12)).grid(
            row=4, column=0, sticky="w", pady=5
        )
        self.profession_entry = Entry(self.main_frame, font=("Arial", 12))
        self.profession_entry.grid(row=4, column=1, pady=5, sticky="nsew")

        # Balance
        Label(self.main_frame, text="Balance:", font=("Arial", 12)).grid(
            row=5, column=0, sticky="w", pady=5
        )
        self.balance_entry = Entry(self.main_frame, font=("Arial", 12))
        self.balance_entry.grid(row=5, column=1, pady=5, sticky="nsew")

        # Password
        Label(self.main_frame, text="Password:", font=("Arial", 12)).grid(
            row=6, column=0, sticky="w", pady=5
        )
        self.password_entry = Entry(self.main_frame, font=("Arial", 12), show="*")
        self.password_entry.grid(row=6, column=1, pady=5, sticky="nsew")

        # Submit Button
        Button(
            self.main_frame,
            text="Add Account",
            font=("Arial", 12, "bold"),
            bg="green",
            fg="white",
            command=self.add_account,
        ).grid(row=7, column=0, columnspan=2, pady=20, sticky="nsew")

        # Configure grid rows and columns to adjust with resizing
        for i in range(1, 7):
            self.main_frame.grid_rowconfigure(i, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=3)

    def insert_accounts_to_database(self, account_data):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="bank",
            )
            cursor = connection.cursor()

            # SQL query to insert account data
            query = """
                INSERT INTO accounts (account_holder, address, phone_number, profession, balance, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    account_data["account_holder"],
                    account_data["address"],
                    account_data["phone_number"],
                    account_data["profession"],
                    account_data["balance"],
                    account_data["password"],
                ),
            )

            connection.commit()
            messagebox.showinfo(
                "Success",
                f"Account created successfully! Account Number: {cursor.lastrowid}",
            )

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_account(self):
        account_holder = self.account_holder_entry.get()
        address = self.address_entry.get()
        phone_number = self.phone_number_entry.get()
        profession = self.profession_entry.get()
        balance = self.balance_entry.get()
        password = self.password_entry.get()

        # Validate input fields
        if not account_holder or not address or not phone_number or not profession or not balance or not password:
            messagebox.showerror("Input Error", "All fields are required!")
            return

        try:
            balance = float(balance)
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            account_data = {
                "account_holder": account_holder,
                "address": address,
                "phone_number": phone_number,
                "profession": profession,
                "balance": balance,
                "password": hashed_password.decode('utf-8'),
            }
            self.insert_accounts_to_database(account_data)
            self.clear_fields()

        except ValueError:
            messagebox.showerror("Input Error", "Balance must be a valid number!")

    def clear_fields(self):
        self.account_holder_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.phone_number_entry.delete(0, "end")
        self.profession_entry.delete(0, "end")
        self.balance_entry.delete(0, "end")
        self.password_entry.delete(0, "end")


# Run the application
if __name__ == "__main__":
    root = Tk()
    app = BankApp(root)
    root.mainloop()
