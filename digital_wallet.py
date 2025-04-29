from interest_calculator import InterestCalculator
from user import BasicUser, SilverUser, GoldUser, User, Transaction
import json
import os
import datetime

class DigitalWallet:
    """Main system class with data persistence"""
    USERS_FILE = "users.json"
    
    def __init__(self):
        self.users = {}
        self.interest_calculator = InterestCalculator(self)
        self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.USERS_FILE):
            try:
                with open(self.USERS_FILE, 'r') as f:
                    users_data = json.load(f)
                    for username, user_data in users_data.items():
                        self.users[username] = User.from_dict(user_data)
                print(f"Loaded {len(self.users)} user(s) from storage")
            except Exception as e:
                print(f"Error loading users: {e}")
                # Create default users if loading fails
                self.create_sample_users()
        else:
            self.create_sample_users()
    
    def save_users(self):
        """Save users to JSON file"""
        users_data = {username: user.to_dict() for username, user in self.users.items()}
        try:
            with open(self.USERS_FILE, 'w') as f:
                json.dump(users_data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def create_sample_users(self):
        """Create sample users if no data file exists"""
        self.register("basic", "pass123", 1)
        self.register("silver", "pass123", 2)
        self.register("gold", "pass123", 3)
        self.deposit("basic", 1000)
        self.deposit("silver", 3000)
        self.deposit("gold", 5000)
        self.save_users()
    
    def start_interest_service(self):
        self.interest_calculator.start()
        print("Interest calculation service started")
    
    def stop_interest_service(self):
        self.interest_calculator.stop()
        print("Interest calculation service stopped")
    
    def register(self, username, password, tier=1):
        if username in self.users:
            print("Username already exists")
            return False
        
        if tier == 1:
            self.users[username] = BasicUser(username, password)
        elif tier == 2:
            self.users[username] = SilverUser(username, password)
        elif tier == 3:
            self.users[username] = GoldUser(username, password)
        else:
            print("Invalid user tier selection")
            return False
        
        print(f"User {username} registered as {self.users[username].tier} tier")
        self.save_users()
        return True
    
    def login(self, username, password):
        if username not in self.users:
            print("User not found")
            return None
        
        user = self.users[username]
        if user.authenticate(username, password):
            print(f"Welcome back, {username} ({user.tier} tier)!")
            return user
        else:
            print("Invalid credentials")
            return None
    
    def process_transfer(self, sender_username, recipient_username, amount):
        if sender_username not in self.users or recipient_username not in self.users:
            print("One or more users not found")
            return False
        
        sender = self.users[sender_username]
        recipient = self.users[recipient_username]
        
        result = sender.transfer(amount, recipient)
        if result:
            self.save_users()
        return result
    
    def deposit(self, username, amount):
        if username not in self.users:
            print("User not found")
            return False
        
        user = self.users[username]
        user.balance += amount
        deposit_transaction = Transaction(amount, "deposit")
        user.transaction_history.append(deposit_transaction)
        user.save_transaction_to_csv(deposit_transaction)
        self.save_users()
        return True
    
    def withdraw(self, username, amount):
        if username not in self.users:
            print("User not found")
            return False
        
        user = self.users[username]
        if user.balance < amount:
            print("Insufficient funds")
            return False
        
        user.balance -= amount
        withdrawal_transaction = Transaction(amount, "withdrawal")
        user.transaction_history.append(withdrawal_transaction)
        user.save_transaction_to_csv(withdrawal_transaction)
        self.save_users()
        return True
    
    def request_loan(self, username, amount):
        if username not in self.users:
            print("User not found")
            return False
        
        user = self.users[username]
        if not isinstance(user, (SilverUser, GoldUser)):
            print("Only Silver and Gold users can request loans")
            return False
        
        result = user.request_loan(amount)
        if result:
            self.save_users()
        return result
    
    def invest(self, username, amount):
        if username not in self.users:
            print("User not found")
            return False
        
        user = self.users[username]
        if not isinstance(user, GoldUser):
            print("Only Gold users can invest")
            return False
        
        result = user.invest(amount)
        if result:
            self.save_users()
        return result

def display_main_menu():
    print("\n=== Digital Wallet System ===")
    print("1. Login")
    print("2. Register")
    print("3. Exit")

def display_tier_options():
    print("\nSelect your account tier:")
    print("1. Basic - $5 fee, $1000 max transfer, 1% APR")
    print("2. Silver - $2 fee, $5000 max transfer, 1.5% APR, $2000 max loan")
    print("3. Gold - No fees, $10000 max transfer, 2% APR, $5000 max loan, Investments")

def display_user_menu(user):
    print(f"\n=== {user.username}'s Wallet ({user.tier} tier) ===")
    print(f"Current Balance: ${user.balance:.2f}")
    print(f"Interest Rate: {user.APR*100:.2f}% APR")
    
    next_interest = datetime.datetime.strptime(user.last_interest_calculation, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=1)
    print(f"Next interest calculation: {next_interest.strftime('%Y-%m-%d %H:%M')}")
    
    print("\n1. Transfer money")
    print("2. Deposit")
    print("3. Withdraw")
    if isinstance(user, (SilverUser, GoldUser)):
        print("4. Request loan")
    if isinstance(user, GoldUser):
        print("5. Invest")
    print("6. View transaction history")
    print("7. Export transactions to CSV")
    print("8. Logout")

def user_session(wallet, user):
    while True:
        display_user_menu(user)
        choice = input("Enter your choice: ")
        
        if choice == "1":
            recipient = input("Recipient username: ")
            amount = float(input("Amount to transfer: "))
            wallet.process_transfer(user.username, recipient, amount)
        
        elif choice == "2":
            amount = float(input("Deposit amount: "))
            wallet.deposit(user.username, amount)
            print(f"${amount:.2f} deposited successfully")
        
        elif choice == "3":
            amount = float(input("Withdrawal amount: "))
            if wallet.withdraw(user.username, amount):
                print(f"${amount:.2f} withdrawn successfully")
        
        elif choice == "4" and isinstance(user, (SilverUser, GoldUser)):
            amount = float(input("Loan amount: "))
            if wallet.request_loan(user.username, amount):
                print(f"Loan of ${amount:.2f} approved")
        
        elif choice == "5" and isinstance(user, GoldUser):
            amount = float(input("Investment amount: "))
            wallet.invest(user.username, amount)
        
        elif choice == "6":
            print("\nTransaction History:")
            transactions = user.view_transactions()
            if not transactions:
                print("No transactions yet")
            else:
                for t in transactions:
                    details = f"{t.timestamp}: {t.type.upper()} ${t.amount:.2f}"
                    if t.recipient:
                        details += f" to {t.recipient}"
                    if t.note:
                        details += f" ({t.note})"
                    print(details)
        
        elif choice == "7":
            filename = f"transactions_{user.username}.csv"
            if user.transaction_history:
                print(f"Transactions exported to {filename}")
            else:
                print("No transactions to export")
        
        elif choice == "8":
            print("Logging out...")
            break
        
        else:
            print("Invalid choice. Please try again.")