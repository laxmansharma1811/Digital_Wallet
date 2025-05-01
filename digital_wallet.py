from interest_calculator import InterestCalculator
from user import User, Transaction
from user_tier import BasicUser, SilverUser, GoldUser, MerchantUser
from kyc_verification import KYCVerification
from fixed_deposit import FixedDeposit
import json
import os
import datetime

class DigitalWallet:
    """Main system class with data persistence"""
    USERS_FILE = "users.json"
    
    def __init__(self):
        self.users = {}
        self.kyc_verifier = KYCVerification()
        self.interest_calculator = InterestCalculator(self)
        self.fixed_deposits = {}
        self.load_users()
        self.load_fixed_deposits()
    
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
    
    def load_fixed_deposits(self):
        """Load fixed deposits from JSON file"""
        if os.path.exists("fixed_deposits.json"):
            try:
                with open("fixed_deposits.json", 'r') as f:
                    deposits_data = json.load(f)
                    for username, deposits in deposits_data.items():
                        self.fixed_deposits[username] = [FixedDeposit.from_dict(d) for d in deposits]
            except Exception as e:
                print(f"Error loading fixed deposits: {e}")
    
    def save_fixed_deposits(self):
        """Save fixed deposits to JSON file"""
        deposits_data = {username: [d.to_dict() for d in deposits] for username, deposits in self.fixed_deposits.items()}
        try:
            with open("fixed_deposits.json", 'w') as f:
                json.dump(deposits_data, f, indent=2)
        except Exception as e:
            print(f"Error saving fixed deposits: {e}")
    
    def create_sample_users(self):
        """Create sample users if no data file exists"""
        sample_kyc = {
            'full_name': 'Sample User',
            'dob': '1990-01-01',
            'address': '123 Sample St',
            'id_number': '123456789'
        }
        self.register("basic", "pass123", 1, sample_kyc)
        self.register("silver", "pass123", 2, sample_kyc)
        self.register("gold", "pass123", 3, sample_kyc)
        self.register("merchant", "pass123", 4, sample_kyc)
        self.deposit("basic", 1000)
        self.deposit("silver", 3000)
        self.deposit("gold", 5000)
        self.deposit("merchant", 10000)
        self.save_users()
    
    def start_interest_service(self):
        self.interest_calculator.start()
        print("Interest calculation service started")
    
    def stop_interest_service(self):
        self.interest_calculator.stop()
        print("Interest calculation service stopped")
    
    def register(self, username, password, tier=1, kyc_data=None):
        if username in self.users:
            print("Username already exists")
            return False
        
        if not kyc_data or not self.kyc_verifier.verify_kyc(username, kyc_data):
            print("KYC verification failed")
            return False
        
        if tier == 1:
            self.users[username] = BasicUser(username, password)
        elif tier == 2:
            self.users[username] = SilverUser(username, password)
        elif tier == 3:
            self.users[username] = GoldUser(username, password)
        elif tier == 4:
            self.users[username] = MerchantUser(username, password)
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
            kyc_status = self.kyc_verifier.get_kyc_status(username)
            print(f"Welcome back, {username} ({user.tier} tier)! KYC Status: {kyc_status}")
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
    
    def process_bulk_payment(self, sender_username, recipients, amount):
        if sender_username not in self.users:
            print("Sender not found")
            return False
        
        sender = self.users[sender_username]
        if not isinstance(sender, MerchantUser):
            print("Only Merchant accounts can process bulk payments")
            return False
        
        for recipient_username in recipients:
            if recipient_username not in self.users:
                print(f"Recipient {recipient_username} not found")
                return False
        
        result = sender.bulk_payment(amount, [self.users[r] for r in recipients])
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
        if not isinstance(user, (SilverUser, GoldUser, MerchantUser)):
            print("Only Silver, Gold, and Merchant users can request loans")
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
    
    def create_fixed_deposit(self, username, amount, term_months):
        if username not in self.users:
            print("User not found")
            return False
        
        user = self.users[username]
        if not isinstance(user, (GoldUser, MerchantUser)):
            print("Only Gold and Merchant users can create fixed deposits")
            return False
        
        if user.balance < amount:
            print("Insufficient funds")
            return False
        
        deposit = FixedDeposit(username, amount, term_months)
        user.balance -= amount
        transaction = Transaction(amount, "fixed_deposit", note=f"Fixed Deposit for {term_months} months")
        user.transaction_history.append(transaction)
        user.save_transaction_to_csv(transaction)
        
        if username not in self.fixed_deposits:
            self.fixed_deposits[username] = []
        self.fixed_deposits[username].append(deposit)
        
        self.save_users()
        self.save_fixed_deposits()
        print(f"Fixed deposit of ${amount:.2f} created for {term_months} months")
        return True
    
    def withdraw_fixed_deposit(self, username, deposit_id):
        if username not in self.users or username not in self.fixed_deposits:
            print("No fixed deposits found")
            return False
        
        user = self.users[username]
        for deposit in self.fixed_deposits[username]:
            if deposit.deposit_id == deposit_id:
                amount, penalty = deposit.withdraw()
                user.balance += amount
                transaction = Transaction(amount, "fixed_deposit_withdrawal", note=f"Fixed Deposit withdrawal, penalty: ${penalty:.2f}")
                user.transaction_history.append(transaction)
                user.save_transaction_to_csv(transaction)
                self.fixed_deposits[username].remove(deposit)
                self.save_users()
                self.save_fixed_deposits()
                print(f"Fixed deposit withdrawn: ${amount:.2f} (Penalty: ${penalty:.2f})")
                return True
        print("Deposit ID not found")
        return False

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
    print("4. Merchant - No fees, $20000 max transfer, 2.5% APR, $10000 max loan, Bulk Payments, Fixed Deposits, $10 monthly fee")

def display_user_menu(wallet, user):
    kyc_status = wallet.kyc_verifier.get_kyc_status(user.username)
    print(f"\n=== {user.username}'s Wallet ({user.tier} tier) ===")
    print(f"Current Balance: ${user.balance:.2f}")
    print(f"Interest Rate: {user.APR*100:.2f}% APR")
    print(f"KYC Status: {kyc_status}")
    
    next_interest = datetime.datetime.strptime(user.last_interest_calculation, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=1)
    print(f"Next interest calculation: {next_interest.strftime('%Y-%m-%d %H:%M')}")
    
    print("\n1. Transfer money")
    print("2. Deposit")
    print("3. Withdraw")
    if isinstance(user, (SilverUser, GoldUser, MerchantUser)):
        print("4. Request loan")
    if isinstance(user, GoldUser):
        print("5. Invest")
    if isinstance(user, MerchantUser):
        print("5. Bulk payment")
    if isinstance(user, (GoldUser, MerchantUser)):
        print("6. Create fixed deposit")
        print("7. Withdraw fixed deposit")
    print("8. View transaction history")
    print("9. Export transactions to CSV")
    print("10. Logout")

def user_session(wallet, user):
    while True:
        display_user_menu(wallet, user)
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
        
        elif choice == "4" and isinstance(user, (SilverUser, GoldUser, MerchantUser)):
            amount = float(input("Loan amount: "))
            if wallet.request_loan(user.username, amount):
                print(f"Loan of ${amount:.2f} approved")
        
        elif choice == "5" and isinstance(user, GoldUser):
            amount = float(input("Investment amount: "))
            wallet.invest(user.username, amount)
        
        elif choice == "5" and isinstance(user, MerchantUser):
            recipients = input("Recipient usernames (comma-separated): ").split(",")
            amount = float(input("Amount per recipient: "))
            wallet.process_bulk_payment(user.username, [r.strip() for r in recipients], amount)
        
        elif choice == "6" and isinstance(user, (GoldUser, MerchantUser)):
            amount = float(input("Deposit amount: "))
            term = int(input("Term in months (3, 6, or 12): "))
            if term not in [3, 6, 12]:
                print("Invalid term. Choose 3, 6, or 12 months")
            else:
                wallet.create_fixed_deposit(user.username, amount, term)
        
        elif choice == "7" and isinstance(user, (GoldUser, MerchantUser)):
            deposit_id = input("Enter deposit ID: ")
            wallet.withdraw_fixed_deposit(user.username, deposit_id)
        
        elif choice == "8":
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
        
        elif choice == "9":
            filename = f"transactions_{user.username}.csv"
            if user.transaction_history:
                print(f"Transactions exported to {filename}")
            else:
                print("No transactions to export")
        
        elif choice == "10":
            print("Logging out...")
            break
        
        else:
            print("Invalid choice. Please try again.")