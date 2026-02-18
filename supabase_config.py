# Supabase Configuration
# Store your Supabase credentials here
# ⚠️ KEEP THIS FILE PRIVATE - Add to .gitignore

import os
import bcrypt
from datetime import datetime

# Try to import streamlit for cloud deployment secrets
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Try to load from Streamlit Cloud secrets first, then fall back to local config
try:
    if HAS_STREAMLIT and hasattr(st, 'secrets') and 'supabase' in st.secrets:
        # Running on Streamlit Cloud - use secrets
        SUPABASE_URL = st.secrets['supabase']['SUPABASE_URL']
        SUPABASE_ANON_KEY = st.secrets['supabase']['SUPABASE_KEY']
        SUPABASE_SERVICE_KEY = st.secrets['supabase'].get('SERVICE_KEY', '')
        DATABASE_PASSWORD = st.secrets['supabase'].get('DATABASE_PASSWORD', '')
    else:
        # Running locally - use hardcoded values
        SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
        SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw"
        # Service role key (get from Supabase Settings → API)
        # Use this for server-side operations (uploads, inserts)
        SUPABASE_SERVICE_KEY = "your-service-role-key-here"
        # Database password (for direct PostgreSQL connection)
        DATABASE_PASSWORD = "554nr1Qh29nPaWoO"
except:
    # Fallback to local values if secrets check fails
    SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw"
    SUPABASE_SERVICE_KEY = "your-service-role-key-here"
    DATABASE_PASSWORD = "554nr1Qh29nPaWoO"


# ==================== AUTHENTICATION FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password as string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        password_hash: Hashed password to check against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False


def login_user(supabase_client, email: str, password: str) -> dict:
    """Authenticate a user with email and password.
    
    Args:
        supabase_client: Supabase client instance
        email: User's email address
        password: User's plain text password
        
    Returns:
        Dict with 'success' (bool), 'message' (str), and 'user' (dict if success)
    """
    try:
        # Query user by email
        response = supabase_client.table('profiles').select('*').eq('email', email).execute()
        
        if not response.data:
            return {
                'success': False,
                'message': 'Invalid email or password',
                'user': None
            }
        
        user = response.data[0]
        
        # Check if account is active
        if not user.get('is_active', True):
            return {
                'success': False,
                'message': 'Account is deactivated. Contact administrator.',
                'user': None
            }
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return {
                'success': False,
                'message': 'Invalid email or password',
                'user': None
            }
        
        # Update last login timestamp
        supabase_client.table('profiles').update({
            'last_login': datetime.utcnow().isoformat()
        }).eq('id', user['id']).execute()
        
        return {
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Login error: {str(e)}',
            'user': None
        }


def register_user(supabase_client, email: str, password: str, full_name: str, role: str = 'user') -> dict:
    """Register a new user.
    
    Args:
        supabase_client: Supabase client instance
        email: User's email address
        password: User's plain text password (will be hashed)
        full_name: User's full name
        role: User role ('user' or 'admin'), defaults to 'user'
        
    Returns:
        Dict with 'success' (bool), 'message' (str), and 'user_id' (str if success)
    """
    try:
        # Validate role
        if role not in ['user', 'admin']:
            return {
                'success': False,
                'message': 'Invalid role. Must be "user" or "admin"',
                'user_id': None
            }
        
        # Check if email already exists
        existing = supabase_client.table('profiles').select('id').eq('email', email).execute()
        if existing.data:
            return {
                'success': False,
                'message': 'Email already registered',
                'user_id': None
            }
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert new user
        response = supabase_client.table('profiles').insert({
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name,
            'role': role,
            'is_active': True
        }).execute()
        
        if response.data:
            return {
                'success': True,
                'message': 'Registration successful',
                'user_id': response.data[0]['id']
            }
        else:
            return {
                'success': False,
                'message': 'Registration failed',
                'user_id': None
            }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Registration error: {str(e)}',
            'user_id': None
        }


def get_user_by_id(supabase_client, user_id: str) -> dict:
    """Retrieve user profile by ID.
    
    Args:
        supabase_client: Supabase client instance
        user_id: User's UUID
        
    Returns:
        User dict if found, None otherwise
    """
    try:
        response = supabase_client.table('profiles').select('*').eq('id', user_id).execute()
        if response.data:
            user = response.data[0]
            # Don't return password hash
            user.pop('password_hash', None)
            return user
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None


