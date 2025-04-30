import json
import os
import datetime
import re

class KYCVerification:
    """Class to handle KYC verification and storage"""
    KYC_FILE = "kyc_data.json"
    
    def __init__(self):
        self.kyc_data = {}
        self.load_kyc_data()
    
    def load_kyc_data(self):
        """Load KYC data from JSON file"""
        if os.path.exists(self.KYC_FILE):
            try:
                with open(self.KYC_FILE, 'r') as f:
                    self.kyc_data = json.load(f)
            except Exception as e:
                print(f"Error loading KYC data: {e}")
    
    def save_kyc_data(self):
        """Save KYC data to JSON file"""
        try:
            with open(self.KYC_FILE, 'w') as f:
                json.dump(self.kyc_data, f, indent=2)
        except Exception as e:
            print(f"Error saving KYC data: {e}")
    
    def verify_kyc(self, username, kyc_info):
        """Verify KYC information"""
        # Basic validation checks
        if not all(key in kyc_info for key in ['full_name', 'dob', 'address', 'id_number']):
            print("Missing required KYC information")
            return False
        
        # Validate full name (simple non-empty check)
        if not kyc_info['full_name'].strip():
            print("Invalid full name")
            return False
        
        # Validate date of birth (YYYY-MM-DD format and reasonable age)
        try:
            dob = datetime.datetime.strptime(kyc_info['dob'], "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
            if age < 18 or age > 120:
                print("Invalid date of birth: Age must be between 18 and 120")
                return False
        except ValueError:
            print("Invalid date of birth format (use YYYY-MM-DD)")
            return False
        
        # Validate address (simple non-empty check)
        if not kyc_info['address'].strip():
            print("Invalid address")
            return False
        
        # Validate ID number (simple format check, e.g., 9 digits)
        if not re.match(r'^\d{9}$', kyc_info['id_number']):
            print("Invalid ID number: Must be 9 digits")
            return False
        
        # Store KYC data
        self.kyc_data[username] = {
            'full_name': kyc_info['full_name'],
            'dob': kyc_info['dob'],
            'address': kyc_info['address'],
            'id_number': kyc_info['id_number'],
            'verified': True,
            'verification_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_kyc_data()
        return True
    
    def get_kyc_status(self, username):
        """Get KYC verification status for a user"""
        if username in self.kyc_data and self.kyc_data[username].get('verified'):
            return "Verified"
        return "Not Verified"