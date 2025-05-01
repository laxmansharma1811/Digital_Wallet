import datetime
import os
import csv

class Transaction:
    """Class to represent transactions including interest payments"""
    def __init__(self, amount, transaction_type, recipient=None, note=""):
        self.amount = amount
        self.type = transaction_type
        self.recipient = recipient
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.note = note

    def to_dict(self):
        """Convert transaction to dictionary for JSON serialization"""
        return {
            'amount': self.amount,
            'type': self.type,
            'recipient': self.recipient,
            'timestamp': self.timestamp,
            'note': self.note
        }

    @classmethod
    def from_dict(cls, data):
        """Create Transaction from dictionary"""
        return cls(
            amount=data['amount'],
            transaction_type=data['type'],
            recipient=data.get('recipient'),
            note=data.get('note', '')
        )

class User:
    """Base user class with core functionality"""
    def __init__(self, username, password, initial_balance=0):
        self.username = username
        self._password = password
        self.balance = initial_balance
        self.transaction_history = []
        self.tier = "Base"
        self.last_interest_calculation = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.APR = 0.02  # Default 2% APR

    def authenticate(self, username, password):
        return self.username == username and self._password == password

    def view_balance(self):
        return self.balance

    def view_transactions(self):
        return self.transaction_history

    def save_transaction_to_csv(self, transaction):
        filename = f"transactions_{self.username}.csv"
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'type', 'amount', 'recipient', 'balance_after', 'tier', 'note']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': transaction.timestamp,
                'type': transaction.type,
                'amount': transaction.amount,
                'recipient': transaction.recipient if transaction.recipient else '',
                'balance_after': self.balance,
                'tier': self.tier,
                'note': transaction.note
            })

    def calculate_daily_interest(self):
        """Calculate and apply daily compound interest"""
        now = datetime.datetime.now()
        last_calc = datetime.datetime.strptime(self.last_interest_calculation, "%Y-%m-%d %H:%M:%S")
        
        if (now - last_calc).days >= 1 and self.balance > 0:
            daily_rate = self.APR / 365
            interest = round(self.balance * daily_rate, 2)
            
            if interest > 0:
                self.balance += interest
                interest_transaction = Transaction(
                    amount=interest,
                    transaction_type="interest",
                    note=f"Daily interest at {self.APR*100:.2f}% APR"
                )
                self.transaction_history.append(interest_transaction)
                self.save_transaction_to_csv(interest_transaction)
                
            self.last_interest_calculation = now.strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """Convert user data to dictionary for JSON serialization"""
        return {
            'username': self.username,
            'password': self._password,
            'balance': self.balance,
            'transaction_history': [t.to_dict() for t in self.transaction_history],
            'tier': self.tier,
            'last_interest_calculation': self.last_interest_calculation,
            'APR': self.APR,
            'last_fee_date': getattr(self, 'last_fee_date', None)
        }

    @classmethod
    def from_dict(cls, data):
        """Create User from dictionary"""
        from user_tier import BasicUser, SilverUser, GoldUser, MerchantUser
        
        user_class = {
            'Basic': BasicUser,
            'Silver': SilverUser,
            'Gold': GoldUser,
            'Merchant': MerchantUser
        }.get(data['tier'], User)
        
        user = user_class(
            username=data['username'],
            password=data['password'],
            initial_balance=data['balance']
        )
        user.transaction_history = [Transaction.from_dict(t) for t in data['transaction_history']]
        user.last_interest_calculation = data['last_interest_calculation']
        user.APR = data.get('APR', 0.02)
        if 'last_fee_date' in data and data['last_fee_date']:
            user.last_fee_date = data['last_fee_date']
        return user