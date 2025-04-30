from Digital_Wallet.user import Transaction
from user_tier import BasicUser, PremiumUser



class DigitalWallet:
    """Main system class that manages users and transactions"""
    def __init__(self):
        self.users = {}
    
    def register(self, username, password, tier="basic"):
        """Factory method pattern - creates appropriate user tier"""
        if username in self.users:
            print("Username already exists")
            return False
        
        if tier.lower() == "basic":
            self.users[username] = BasicUser(username, password)
        elif tier.lower() == "premium":
            self.users[username] = PremiumUser(username, password)
        else:
            print("Invalid user tier")
            return False
        
        print(f"User {username} registered as {tier} tier")
        return True
    
    def login(self, username, password):
        if username not in self.users:
            print("User not found")
            return None
        
        user = self.users[username]
        if user.authenticate(username, password):
            print(f"Welcome back, {username}!")
            return user
        else:
            print("Invalid credentials")
            return None
    
    def process_transaction(self, sender_username, recipient_username, amount):
        if sender_username not in self.users or recipient_username not in self.users:
            print("One or more users not found")
            return False
        
        sender = self.users[sender_username]
        recipient = self.users[recipient_username]
        
        return sender.transfer(amount, recipient)
    

    def deposit(self, username, amount):
        if username not in self.users:
            print("User not found")
            return False
        
        user = self.users[username]
        user.balance += amount
        user.transaction_history.append(Transaction(amount, "deposit"))
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
        user.transaction_history.append(Transaction(amount, "withdrawal"))
        return True
    
    def request_loan(self, username, amount):
        if username not in self.users:
            print("User not found")
            return False
        
        user = self.users[username]
        if not isinstance(user, PremiumUser):
            print("Only premium users can request loans")
            return False
        
        return user.request_loan(amount)
    

def main():
    wallet = DigitalWallet()
    
    # Register some sample users
    wallet.register("alice", "password123", "basic")
    wallet.register("bob", "securepass", "premium")
    
    # Make some deposits
    wallet.deposit("alice", 500)
    wallet.deposit("bob", 1500)
    
    while True:
        print("\nDigital Wallet System")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            username = input("Username: ")
            password = input("Password: ")
            user = wallet.login(username, password)
            
            if user:
                user_menu(wallet, user)
        
        elif choice == "2":
            username = input("Choose a username: ")
            password = input("Choose a password: ")
            tier = input("Choose tier (basic/premium): ")
            wallet.register(username, password, tier)
        
        elif choice == "3":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")

def user_menu(wallet, user):
    while True:
        print(f"\nWelcome, {user.username} ({user.tier} tier)")
        print(f"Balance: ${user.balance}")
        print("1. Transfer money")
        print("2. Deposit")
        print("3. Withdraw")
        if isinstance(user, PremiumUser):
            print("4. Request loan")
        print("5. View transaction history")
        print("6. Logout")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            recipient = input("Recipient username: ")
            amount = float(input("Amount: "))
            wallet.process_transaction(user.username, recipient, amount)
        
        elif choice == "2":
            amount = float(input("Deposit amount: "))
            wallet.deposit(user.username, amount)
        
        elif choice == "3":
            amount = float(input("Withdrawal amount: "))
            wallet.withdraw(user.username, amount)
        
        elif choice == "4" and isinstance(user, PremiumUser):
            amount = float(input("Loan amount: "))
            wallet.request_loan(user.username, amount)
        
        elif choice == "5":
            print("\nTransaction History:")
            for t in user.view_transactions():
                details = f"{t.timestamp}: {t.type} ${t.amount}"
                if t.recipient:
                    details += f" to {t.recipient}"
                print(details)
        
        elif choice == "6":
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    import datetime  # Needed for transaction timestamps
    main()