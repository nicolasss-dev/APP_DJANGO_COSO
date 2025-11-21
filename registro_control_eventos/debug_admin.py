import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registro_control_eventos.settings')
django.setup()

from usuarios.models import Usuario

def debug_admin_user():
    print("Debugging admin user...")
    
    try:
        admin = Usuario.objects.get(email='admin@example.com')
        print(f"User found: {admin.username}")
        print(f"Active: {admin.activo}")
        print(f"Is Staff: {admin.is_staff}")
        print(f"Is Superuser: {admin.is_superuser}")
        print(f"Failed Attempts: {admin.intentos_fallidos}")
        print(f"Blocked Until: {admin.bloqueado_hasta}")
        
        if admin.esta_bloqueado():
            print("WARNING: User is currently BLOCKED.")
            print("Unblocking user...")
            admin.resetear_intentos_fallidos()
            print("User unblocked.")
            
        # Reset password just in case
        print("Resetting password to 'admin123'...")
        admin.set_password('admin123')
        admin.save()
        print("Password reset successful.")
        
    except Usuario.DoesNotExist:
        print("ERROR: Admin user not found!")

if __name__ == '__main__':
    debug_admin_user()
