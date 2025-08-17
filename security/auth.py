"""
Authentication and authorization system
"""
import hashlib
import hmac
import base64
import secrets
from typing import Dict, Optional
import json
import os
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, auth_file: str = "data/auth.json"):
        self.auth_file = auth_file
        self._load_auth_data()
        self._setup_auth_system()
    
    def _load_auth_data(self):
        """Load authentication data"""
        if not os.path.exists(self.auth_file):
            self._create_default_auth()
        
        with open(self.auth_file, 'r') as f:
            self.auth_data = json.load(f)
    
    def _create_default_auth(self):
        """Create default authentication data"""
        default_auth = {
            "users": {
                "admin": {
                    "password_hash": self._hash_password("admin123"),
                    "roles": ["admin", "user"],
                    "last_login": None,
                    "api_key": self._generate_api_key()
                }
            },
            "api_keys": {},
            "permissions": {
                "admin": ["all"],
                "user": ["scan", "report"]
            }
        }
        
        os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
        with open(self.auth_file, 'w') as f:
            json.dump(default_auth, f, indent=4)
    
    def _hash_password(self, password: str) -> str:
        """Securely hash password"""
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${base64.b64encode(key).decode('utf-8')}"
    
    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        if username not in self.auth_data["users"]:
            return False
            
        stored = self.auth_data["users"][username]["password_hash"]
        salt, stored_key = stored.split('$')
        
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return hmac.compare_digest(
            base64.b64encode(key).decode('utf-8'),
            stored_key
        )
    
    def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """Verify API key and return user info"""
        for user, data in self.auth_data["users"].items():
            if data["api_key"] == api_key:
                return {
                    "username": user,
                    "roles": data["roles"],
                    "permissions": self.get_user_permissions(user)
                }
        return None
    
    def get_user_permissions(self, username: str) -> List[str]:
        """Get user permissions"""
        if username not in self.auth_data["users"]:
            return []
            
        roles = self.auth_data["users"][username]["roles"]
        permissions = set()
        
        for role in roles:
            if role in self.auth_data["permissions"]:
                permissions.update(self.auth_data["permissions"][role])
        
        return list(permissions)
    
    def generate_session_token(self, username: str) -> str:
        """Generate secure session token"""
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=24)
        
        self.auth_data["users"][username]["last_login"] = datetime.now().isoformat()
        self._save_auth_data()
        
        return f"{token}${expiry.isoformat()}"
    
    def validate_session(self, token: str) -> bool:
        """Validate session token"""
        try:
            token_parts = token.split('$')
            if len(token_parts) != 2:
                return False
            
            expiry = datetime.fromisoformat(token_parts[1])
            return expiry > datetime.now()
        except Exception:
            return False
    
    def _save_auth_data(self):
        """Save authentication data"""
        with open(self.auth_file, 'w') as f:
            json.dump(self.auth_data, f, indent=4)
    
    def add_user(self, username: str, password: str, roles: List[str] = ["user"]):
        """Add new user"""
        if username in self.auth_data["users"]:
            raise ValueError("User already exists")
            
        self.auth_data["users"][username] = {
            "password_hash": self._hash_password(password),
            "roles": roles,
            "last_login": None,
            "api_key": self._generate_api_key()
        }
        self._save_auth_data()
    
    def remove_user(self, username: str):
        """Remove user"""
        if username not in self.auth_data["users"]:
            raise ValueError("User does not exist")
            
        del self.auth_data["users"][username]
        self._save_auth_data()
