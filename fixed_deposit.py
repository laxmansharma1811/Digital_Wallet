import datetime
import uuid

class FixedDeposit:
    """Class to handle fixed deposit accounts"""
    TERM_APR = {
        3: 0.03,   # 3% APR for 3 months
        6: 0.04,   # 4% APR for 6 months
        12: 0.05   # 5% APR for 12 months
    }
    
    def __init__(self, username, amount, term_months):
        self.deposit_id = str(uuid.uuid4())
        self.username = username
        self.amount = amount
        self.term_months = term_months
        self.apr = self.TERM_APR[term_months]
        self.start_date = datetime.datetime.now()
        self.maturity_date = self.start_date + datetime.timedelta(days=term_months * 30)
        self.early_withdrawal_penalty = 0.01  # 1% penalty for early withdrawal
    
    def calculate_interest(self):
        """Calculate total amount with compound interest at maturity"""
        days = (self.maturity_date - self.start_date).days
        daily_rate = self.apr / 365
        total = self.amount * (1 + daily_rate) ** days
        return round(total, 2)
    
    def withdraw(self):
        """Withdraw fixed deposit, applying penalty if before maturity"""
        now = datetime.datetime.now()
        penalty = 0
        amount = self.amount
        
        if now < self.maturity_date:
            penalty = round(self.amount * self.early_withdrawal_penalty, 2)
            amount -= penalty
        else:
            amount = self.calculate_interest()
        
        return amount, penalty
    
    def to_dict(self):
        """Convert fixed deposit to dictionary for JSON serialization"""
        return {
            'deposit_id': self.deposit_id,
            'username': self.username,
            'amount': self.amount,
            'term_months': self.term_months,
            'apr': self.apr,
            'start_date': self.start_date.strftime("%Y-%m-%d %H:%M:%S"),
            'maturity_date': self.maturity_date.strftime("%Y-%m-%d %H:%M:%S"),
            'early_withdrawal_penalty': self.early_withdrawal_penalty
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create FixedDeposit from dictionary"""
        deposit = cls(data['username'], data['amount'], data['term_months'])
        deposit.deposit_id = data['deposit_id']
        deposit.apr = data['apr']
        deposit.start_date = datetime.datetime.strptime(data['start_date'], "%Y-%m-%d %H:%M:%S")
        deposit.maturity_date = datetime.datetime.strptime(data['maturity_date'], "%Y-%m-%d %H:%M:%S")
        deposit.early_withdrawal_penalty = data['early_withdrawal_penalty']
        return deposit