from user import Transaction, User
import datetime

class BasicUser(User):
    """Basic user tier with limited features"""
    MAX_TRANSACTION = 1000
    TRANSACTION_FEE = 5
    
    def __init__(self, username, password, initial_balance=0):
        super().__init__(username, password, initial_balance)
        self.tier = "Basic"
        self.APR = 0.01  # 1% APR
    
    def transfer(self, amount, recipient):
        total_amount = amount + self.TRANSACTION_FEE
        if amount > self.MAX_TRANSACTION:
            print(f"Error: Basic users can't transfer more than ${self.MAX_TRANSACTION}")
            return False
        if self.balance < total_amount:
            print(f"Insufficient funds (including ${self.TRANSACTION_FEE} fee)")
            return False
        
        self.balance -= total_amount
        recipient.balance += amount
        
        out_transaction = Transaction(amount, "transfer_out", recipient.username)
        in_transaction = Transaction(amount, "transfer_in", self.username)
        
        self.transaction_history.append(out_transaction)
        recipient.transaction_history.append(in_transaction)
        
        self.save_transaction_to_csv(out_transaction)
        recipient.save_transaction_to_csv(in_transaction)
        
        fee_transaction = Transaction(self.TRANSACTION_FEE, "fee", note="Transfer fee")
        self.transaction_history.append(fee_transaction)
        self.save_transaction_to_csv(fee_transaction)
        
        return True

class SilverUser(User):
    """Silver user tier with more features"""
    MAX_TRANSACTION = 5000
    TRANSACTION_FEE = 2
    
    def __init__(self, username, password, initial_balance=0):
        super().__init__(username, password, initial_balance)
        self.tier = "Silver"
        self.APR = 0.015  # 1.5% APR
    
    def transfer(self, amount, recipient):
        total_amount = amount + self.TRANSACTION_FEE
        if amount > self.MAX_TRANSACTION:
            print(f"Error: Silver users can't transfer more than ${self.MAX_TRANSACTION}")
            return False
        if self.balance < total_amount:
            print(f"Insufficient funds (including ${self.TRANSACTION_FEE} fee)")
            return False
        
        self.balance -= total_amount
        recipient.balance += amount
        
        out_transaction = Transaction(amount, "transfer_out", recipient.username)
        in_transaction = Transaction(amount, "transfer_in", self.username)
        
        self.transaction_history.append(out_transaction)
        recipient.transaction_history.append(in_transaction)
        
        self.save_transaction_to_csv(out_transaction)
        recipient.save_transaction_to_csv(in_transaction)
        
        fee_transaction = Transaction(self.TRANSACTION_FEE, "fee", note="Transfer fee")
        self.transaction_history.append(fee_transaction)
        self.save_transaction_to_csv(fee_transaction)
        
        return True
    
    def request_loan(self, amount):
        if amount > 2000:
            print("Loan request denied: Maximum loan is $2000 for Silver users")
            return False
        
        self.balance += amount
        loan_transaction = Transaction(amount, "loan", note="Silver tier loan")
        self.transaction_history.append(loan_transaction)
        self.save_transaction_to_csv(loan_transaction)
        return True

class GoldUser(User):
    """Gold user tier with premium features"""
    MAX_TRANSACTION = 10000
    TRANSACTION_FEE = 0
    
    def __init__(self, username, password, initial_balance=0):
        super().__init__(username, password, initial_balance)
        self.tier = "Gold"
        self.APR = 0.02  # 2% APR
    
    def transfer(self, amount, recipient):
        if amount > self.MAX_TRANSACTION:
            print(f"Error: Gold users can't transfer more than ${self.MAX_TRANSACTION}")
            return False
        if self.balance < amount:
            print("Insufficient funds")
            return False
        
        self.balance -= amount
        recipient.balance += amount
        
        out_transaction = Transaction(amount, "transfer_out", recipient.username)
        in_transaction = Transaction(amount, "transfer_in", self.username)
        
        self.transaction_history.append(out_transaction)
        recipient.transaction_history.append(in_transaction)
        
        self.save_transaction_to_csv(out_transaction)
        recipient.save_transaction_to_csv(in_transaction)
        
        return True
    
    def request_loan(self, amount):
        if amount > 5000:
            print("Loan request denied: Maximum loan is $5000 for Gold users")
            return False
        
        self.balance += amount
        loan_transaction = Transaction(amount, "loan", note="Gold tier loan")
        self.transaction_history.append(loan_transaction)
        self.save_transaction_to_csv(loan_transaction)
        return True
    
    def invest(self, amount):
        if amount > self.balance:
            print("Insufficient funds for investment")
            return False
        
        self.balance -= amount
        import random
        if random.random() < 0.6:
            return_amount = round(amount * 1.05, 2)
            self.balance += return_amount
            invest_transaction = Transaction(amount, "investment_out")
            return_transaction = Transaction(return_amount - amount, "investment_profit")
            self.transaction_history.extend([invest_transaction, return_transaction])
            self.save_transaction_to_csv(invest_transaction)
            self.save_transaction_to_csv(return_transaction)
            print(f"Investment successful! You earned ${return_amount - amount:.2f}")
        else:
            invest_transaction = Transaction(amount, "investment_loss")
            self.transaction_history.append(invest_transaction)
            self.save_transaction_to_csv(invest_transaction)
            print("Investment didn't yield returns this time")
        return True

class MerchantUser(User):
    """Merchant user tier for business accounts"""
    MAX_TRANSACTION = 20000
    TRANSACTION_FEE = 0
    MONTHLY_FEE = 10
    
    def __init__(self, username, password, initial_balance=0):
        super().__init__(username, password, initial_balance)
        self.tier = "Merchant"
        self.APR = 0.025  # 2.5% APR
        self.last_fee_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    def transfer(self, amount, recipient):
        if amount > self.MAX_TRANSACTION:
            print(f"Error: Merchant users can't transfer more than ${self.MAX_TRANSACTION}")
            return False
        if self.balance < amount:
            print("Insufficient funds")
            return False
        
        self.balance -= amount
        recipient.balance += amount
        
        out_transaction = Transaction(amount, "transfer_out", recipient.username)
        in_transaction = Transaction(amount, "transfer_in", self.username)
        
        self.transaction_history.append(out_transaction)
        recipient.transaction_history.append(in_transaction)
        
        self.save_transaction_to_csv(out_transaction)
        recipient.save_transaction_to_csv(in_transaction)
        
        return True
    
    def bulk_payment(self, amount, recipients):
        total_amount = amount * len(recipients)
        if total_amount > self.balance:
            print("Insufficient funds for bulk payment")
            return False
        
        self.balance -= total_amount
        for recipient in recipients:
            recipient.balance += amount
            out_transaction = Transaction(amount, "bulk_payment_out", recipient.username)
            in_transaction = Transaction(amount, "bulk_payment_in", self.username)
            self.transaction_history.append(out_transaction)
            recipient.transaction_history.append(in_transaction)
            self.save_transaction_to_csv(out_transaction)
            recipient.save_transaction_to_csv(in_transaction)
        
        return True
    
    def request_loan(self, amount):
        if amount > 10000:
            print("Loan request denied: Maximum loan is $10000 for Merchant users")
            return False
        
        self.balance += amount
        loan_transaction = Transaction(amount, "loan", note="Merchant tier loan")
        self.transaction_history.append(loan_transaction)
        self.save_transaction_to_csv(loan_transaction)
        return True
    
    def calculate_daily_interest(self):
        """Calculate daily interest and monthly maintenance fee"""
        super().calculate_daily_interest()
        
        now = datetime.datetime.now()
        last_fee = datetime.datetime.strptime(self.last_fee_date, "%YB-%Y-%m-%d")
        if (now - last_fee).days >= 30:  # Check if a month has passed
            if self.balance >= self.MONTHLY_FEE:
                self.balance -= self.MONTHLY_FEE
                fee_transaction = Transaction(self.MONTHLY_FEE, "maintenance_fee", note="Monthly Merchant account fee")
                self.transaction_history.append(fee_transaction)
                self.save_transaction_to_csv(fee_transaction)
                self.last_fee_date = now.strftime("%Y-%m-%d")