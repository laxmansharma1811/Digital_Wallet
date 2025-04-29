from getpass import getpass
import time
from digital_wallet import DigitalWallet, display_main_menu, user_session
from user_tier import UserTier, display_tier_options


def main():
    wallet = DigitalWallet()
    wallet.start_interest_service()
    
    try:
        while True:
            display_main_menu()
            choice = input("Enter your choice (1-3): ")
            
            if choice == "1":
                username = input("Username: ")
                password = getpass("Password: ")
                user = wallet.login(username, password)
                
                if user:
                    user_session(wallet, user)
            
            elif choice == "2":
                username = input("Choose a username: ")
                password = getpass("Choose a password: ")
                display_tier_options()
                tier_choice = input("Select tier (1-3): ")
                
                try:
                    tier = int(tier_choice)
                    if tier not in [1, 2, 3]:
                        raise ValueError
                    wallet.register(username, password, tier)
                    deposit_amount = float(input("Initial deposit amount: $"))
                    wallet.deposit(username, deposit_amount)
                except ValueError:
                    print("Invalid tier selection. Please enter 1, 2, or 3")
            
            elif choice == "3":
                wallet.stop_interest_service()
                print("Thank you for using the Digital Wallet System. Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        wallet.stop_interest_service()
        print("\nSystem shutdown gracefully")

if __name__ == "__main__":
    main()