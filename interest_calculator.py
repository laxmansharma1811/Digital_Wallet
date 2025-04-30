import datetime
from threading import Timer


class InterestCalculator:
    """Background service to calculate interest daily"""
    def __init__(self, wallet, interval=60):  # Default: 60 seconds for demo
        self.wallet = wallet
        self.interval = interval
        self.is_running = False
        self.timer = None
        
    def start(self):
        if not self.is_running:
            self.is_running = True
            self.run()
    
    def run(self):
        if self.is_running:
            now = datetime.datetime.now()
            print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Calculating daily interest...")
            for user in self.wallet.users.values():
                user.calculate_daily_interest()
            self.wallet.save_users()  # Save after interest calculation
            self.timer = Timer(self.interval, self.run)
            self.timer.start()
    
    def stop(self):
        self.is_running = False
        if self.timer:
            self.timer.cancel()