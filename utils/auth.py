from flask import session, redirect, url_for, request
from functools import wraps
import hashlib
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from utils.db import get_db_connection

def hash_password(password):
    """Generar hash seguro de contraseña"""
    return generate_password_hash(password, method='scrypt')

def verify_password(password, password_hash):
    """Verificar contraseña contra hash"""
    return check_password_hash(password_hash, password)

def authenticate_user(username, password):
    """Autenticar usuario"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash, nombre, rol, activo FROM usuarios WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and user[5] and verify_password(password, user[2]):
            return {
                'id': user[0],
                'username': user[1],
                'nombre': user[3],
                'rol': user[4]
            }
        return None
    except Exception as e:
        print(f"Error autenticando: {e}")
        return None

def login_required(roles=None):
    """Decorador para requerir login y roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login_page', next=request.url))
            
            if roles and session.get('rol') not in roles:
                return "Acceso denegado. No tiene permisos suficientes.", 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Obtener usuario actual de la sesión"""
    return session.get('user')

def is_admin():
    """Verificar si es administrador"""
    return session.get('rol') == 'admin'

def is_vendedor():
    """Verificar si es vendedor"""
    return session.get('rol') in ['admin', 'vendedor']
