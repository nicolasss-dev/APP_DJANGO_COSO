"""
Vistas para la aplicación de Usuarios
HU-04: Inicio de Sesión
HU-11: Creación de Usuarios
HU-13: Edición de Perfil
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Usuario, HistorialCambioRol
from .forms import LoginForm, UsuarioForm, PerfilForm, RegistroPublicoForm, RecuperarPasswordForm


import logging
from django.utils.http import url_has_allowed_host_and_scheme

logger = logging.getLogger(__name__)

def login_view(request):
    """
    Vista de inicio de sesión (HU-04)
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Intentar autenticar (puede ser username o email)
            user = authenticate(request, username=username, password=password)
            
            # Si no funciona con username, intentar con email
            if user is None:
                try:
                    user_obj = Usuario.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except Usuario.DoesNotExist:
                    pass
            
            if user is not None:
                # Verificar si puede iniciar sesión (HU-04: cuenta activa y no bloqueada)
                if not user.puede_iniciar_sesion():
                    if user.esta_bloqueado():
                        logger.warning(f'Intento de login de usuario bloqueado: {username}')
                        messages.error(
                            request,
                            'Su cuenta ha sido bloqueada temporalmente por múltiples intentos fallidos. '
                            'Por favor intente nuevamente en 15 minutos.'
                        )
                    else:
                        logger.warning(f'Intento de login de usuario desactivado: {username}')
                        messages.error(
                            request,
                            'Su cuenta ha sido desactivada. Contacte al administrador.'
                        )
                    return render(request, 'usuarios/login.html', {'form': form})
                
                # Login exitoso
                login(request, user)
                logger.info(f'Login exitoso: {user.username}')
                
                # Configurar sesión según "Recordarme"
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 semanas
                else:
                    request.session.set_expiry(1200)  # 20 minutos
                
                user.resetear_intentos_fallidos()
                user.registrar_acceso()
                
                messages.success(request, f'Bienvenido, {user.get_full_name() or user.username}!')
                
                # Redirigir según rol de forma segura
                next_url = request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure()
                ):
                    return redirect(next_url)
                return redirect('dashboard:index')
            else:
                # Credenciales inválidas
                logger.warning(f'Login fallido para: {username}')
                # Intentar encontrar el usuario para incrementar intentos fallidos
                try:
                    user = Usuario.objects.get(username=username)
                    user.incrementar_intentos_fallidos()
                except Usuario.DoesNotExist:
                    try:
                        user = Usuario.objects.get(email=username)
                        user.incrementar_intentos_fallidos()
                    except Usuario.DoesNotExist:
                        pass
                
                messages.error(request, 'Usuario o contraseña inválidos')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.info(request, 'Ha cerrado sesión correctamente')
    return redirect('usuarios:login')


@login_required
def perfil_view(request):
    """
    Vista de perfil de usuario (HU-13)
    Muestra información del usuario y sus eventos próximos
    """
    from inscripciones.models import Inscripcion
    from django.db.models import Q
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Perfil actualizado correctamente')
                return redirect('usuarios:perfil')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error al actualizar perfil: {str(e)}')
                messages.error(request, f'Error al actualizar perfil: {str(e)}')
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = form.fields[field].label if field in form.fields else field
                        messages.error(request, f'{field_name}: {error}')
    else:
        form = PerfilForm(instance=request.user)
    
    # Obtener inscripciones del usuario a eventos futuros
    inscripciones_proximas = Inscripcion.objects.filter(
        Q(usuario=request.user) | Q(correo=request.user.email),
        evento__fecha_inicio__gte=timezone.now(),
        estado__in=['CONFIRMADA', 'PENDIENTE']
    ).select_related('evento', 'evento__tipo_evento').order_by('evento__fecha_inicio')[:5]
    
    # Obtener historial de eventos pasados
    inscripciones_pasadas = Inscripcion.objects.filter(
        Q(usuario=request.user) | Q(correo=request.user.email),
        evento__fecha_fin__lt=timezone.now(),
        estado='CONFIRMADA'
    ).select_related('evento').order_by('-evento__fecha_fin')[:5]
    
    context = {
        'form': form,
        'inscripciones_proximas': inscripciones_proximas,
        'inscripciones_pasadas': inscripciones_pasadas,
        'total_inscripciones': inscripciones_proximas.count() + inscripciones_pasadas.count()
    }
    
    return render(request, 'usuarios/perfil.html', context)


@login_required
def lista_usuarios(request):
    """
    Lista de usuarios (solo Administradores)
    """
    if not request.user.es_administrador():
        messages.error(request, 'No tiene permisos para acceder a esta página')
        return redirect('dashboard')
    
    usuarios = Usuario.objects.all().order_by('-fecha_registro')
    
    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios
    })


@login_required
def crear_usuario(request):
    """
    Crear nuevo usuario (HU-11 - solo Administradores)
    """
    if not request.user.es_administrador():
        messages.error(request, 'No tiene permisos para acceder a esta página')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.save()
            
            # Enviar correo con credenciales (HU-11)
            # TODO: Implementar envío de correo
            
            messages.success(request, 'Usuario creado exitosamente')
            return redirect('usuarios:lista')
    else:
        form = UsuarioForm()
    
    return render(request, 'usuarios/crear.html', {'form': form})


@login_required
def editar_usuario(request, pk):
    """
    Editar usuario (solo Administradores)
    """
    if not request.user.es_administrador():
        messages.error(request, 'No tiene permisos para acceder a esta página')
        return redirect('dashboard')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        rol_anterior = usuario.rol
        form = UsuarioForm(request.POST, instance=usuario)
        
        if form.is_valid():
            usuario = form.save()
            
            # Registrar cambio de rol si aplica (HU-12)
            if rol_anterior != usuario.rol:
                HistorialCambioRol.objects.create(
                    usuario=usuario,
                    rol_anterior=rol_anterior,
                    rol_nuevo=usuario.rol,
                    cambiado_por=request.user
                )
            
            messages.success(request, 'Usuario actualizado correctamente')
            return redirect('usuarios:lista')
    else:
        form = UsuarioForm(instance=usuario)
    
    return render(request, 'usuarios/editar.html', {
        'form': form,
        'usuario': usuario
    })


@login_required
def activar_desactivar_usuario(request, pk):
    """
    Activar o desactivar usuario (HU-14 - solo Administradores)
    """
    if not request.user.es_administrador():
        messages.error(request, 'No tiene permisos para realizar esta acción')
        return redirect('dashboard')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # No permitir que un admin se desactive a sí mismo
    if usuario == request.user and usuario.es_administrador():
        messages.error(request, 'No puede desactivar su propia cuenta de administrador')
        return redirect('usuarios:lista')
    
    if usuario.activo:
        usuario.desactivar(usuario_modificador=request.user)
        messages.success(request, f'Usuario {usuario.username} desactivado correctamente')
    else:
        usuario.activar(usuario_modificador=request.user)
        messages.success(request, f'Usuario {usuario.username} activado correctamente')
    
    return redirect('usuarios:lista')


def registro_publico(request):
    """
    Vista pública de registro de usuarios (HU-04)
    Permite a usuarios externos crear cuenta como ASISTENTE
    """
    if request.user.is_authenticated:
        messages.info(request, 'Ya tiene una sesión activa')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = RegistroPublicoForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save()
                messages.success(
                    request,
                    f'¡Cuenta creada exitosamente! Bienvenido, {usuario.get_full_name()}. '
                    f'Ahora puede iniciar sesión.'
                )
                # TODO: Enviar correo de confirmación
                return redirect('usuarios:login')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error en registro público: {str(e)}')
                messages.error(
                    request,
                    f'Ocurrió un error al crear su cuenta: {str(e)}. '
                    f'Por favor intente nuevamente.'
                )
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = form.fields[field].label if field in form.fields else field
                        messages.error(request, f'{field_name}: {error}')
    else:
        form = RegistroPublicoForm()
    
    return render(request, 'usuarios/registro_publico.html', {'form': form})


def recuperar_password(request):
    """
    Vista para recuperar contraseña (HU-33)
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                usuario = Usuario.objects.get(email=email)
                # TODO: Generar token y enviar correo
                # Por ahora, solo mostrar mensaje
                messages.success(
                    request,
                    'Si el correo existe en nuestro sistema, se ha enviado un enlace para recuperar su contraseña. '
                    'Revise su bandeja de entrada y carpeta de spam.'
                )
            except Usuario.DoesNotExist:
                # Por seguridad, no revelar si el email existe
                messages.success(
                    request,
                    'Si el correo existe en nuestro sistema, se ha enviado un enlace para recuperar su contraseña. '
                    'Revise su bandeja de entrada y carpeta de spam.'
                )
            
            return redirect('usuarios:login')
    else:
        form = RecuperarPasswordForm()
    
    return render(request, 'usuarios/recuperar_password.html', {'form': form})
