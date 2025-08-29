from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import UserProfile

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['user_id'] = user.id
        token['username'] = user.username

        return token

    def get_permissions(user):
        """
        Retorna todos los permisos (codenames) asignados al usuario, tanto directos como heredados por grupos.
        """
        all_perms = set()  # usamos set para evitar duplicados

        # Permisos heredados por grupos
        group_perms = user.get_group_permissions()

        # Permisos asignados directamente
        direct_perms = user.user_permissions.values_list('codename', flat=True)

        # Normalizamos todos a codenames
        for perm in group_perms:
            all_perms.add(perm.split('.')[-1])  # de "app_label.codename" → "codename"
        for codename in direct_perms:
            all_perms.add(codename)

        return list(all_perms)


class UserWithRolesSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name'
    )
    user_permissions = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='codename'
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups', 'user_permissions']


class UserProfileSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    
    class Meta:
        model = UserProfile
        fields = ['id', 'photo_sharepoint_url', 'photo_url', 'phone', 'created', 'modified']
        read_only_fields = ['created', 'modified']
    
    def get_photo_url(self, obj):
        if obj.photo_sharepoint_url:
            filename = obj.photo_sharepoint_url.split('/')[-1]
            proxy_url = f"/api/users/photo/{filename}"
            return proxy_url
        return None


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    roles = serializers.SlugRelatedField(
        source='groups', slug_field='name', many=True, read_only=True
    )

    # Permissions y workCells
    permissions = serializers.SerializerMethodField()
    workCells = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'profile',
                  'roles', 'permissions', 'workCells']

    def get_permissions(self, obj):
        return MyTokenObtainPairSerializer.get_permissions(obj)

    def get_workCells(self, obj):
        return [
            {
                'id': wc.id,
                'name': wc.name,
            }
            for wc in obj.workcell.all()
        ]


class UserWithWorkcellSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    workcells = serializers.SerializerMethodField()
    workcell_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_active', 'workcells', 'workcell_count', 'profile']

    def get_workcells(self, obj):
        """Devuelve las WorkCells asignadas al usuario"""
        return [
            {
                'id': wc.id,
                'name': wc.name,
            }
            for wc in obj.workcell.all()
        ]

    def get_workcell_count(self, obj):
        """Cuenta las WorkCells asignadas"""
        return obj.workcell.count()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        profile = instance.profile
        profile.phone = validated_data.get('phone', profile.phone)
        profile.save()

        return instance


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'required': 'La nueva contraseña es obligatoria.',
            'min_length': 'La contraseña debe tener al menos 8 caracteres.'
        }
    )
    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': 'Debe confirmar la nueva contraseña.'
        }
    )

    def validate_new_password(self, value):
        """Validar la nueva contraseña usando los validadores de Django"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        """Validar que las contraseñas coincidan"""
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden.'
            })

        return data

    def save(self, user):
        """Actualizar la contraseña del usuario"""
        password = self.validated_data['new_password']
        user.set_password(password)
        user.save()
        return user


class ProfilePhotoUploadSerializer(serializers.Serializer):
    photo = serializers.ImageField(
        required=True,
        error_messages={
            'required': 'La foto es obligatoria.',
            'invalid': 'El archivo debe ser una imagen válida.'
        }
    )

    def validate_photo(self, value):
        # Validar tamaño (máximo 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("La imagen no puede superar 5MB")

        # Validar formato
        allowed_formats = ['jpeg', 'jpg', 'png', 'webp']
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in allowed_formats:
            raise serializers.ValidationError(f"Formato no permitido. Use: {', '.join(allowed_formats)}")

        return value
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingrese un correo electrónico válido.'
        }
    )

    def validate_email(self, value):
        """Verificar que el email existe en el sistema"""
        try:
            user = User.objects.get(email=value, is_active=True)
            return value
        except User.DoesNotExist:
            # Por seguridad, no revelar si el email existe o no
            # Pero internamente no enviaremos email
            return value

    def save(self):
        """Enviar email de reset si el usuario existe"""
        email = self.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generar token y UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # URL de reset (ajustar según tu frontend)
            reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{uid}/{token}/"
            
            # Contexto para el template
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'Ferbaq Opportunity Manager',
                'company_name': 'FERBAQ',
            }
            
            # Renderizar template HTML
            html_message = render_to_string('emails/password_reset.html', context)
            plain_message = render_to_string('emails/password_reset.txt', context)
            
            # Enviar email
            send_mail(
                subject='Restablecimiento de contraseña - Ferbaq Opportunity Manager',
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return True
            
        except User.DoesNotExist:
            # Usuario no existe, pero devolvemos True por seguridad
            return True
        except Exception as e:
            # Log del error pero no exponer detalles
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error enviando email de reset: {e}")
            return False


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'required': 'La nueva contraseña es obligatoria.',
            'min_length': 'La contraseña debe tener al menos 8 caracteres.'
        }
    )
    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': 'Debe confirmar la nueva contraseña.'
        }
    )

    def validate_new_password(self, value):
        """Validar la nueva contraseña"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        """Validar que las contraseñas coincidan y el token sea válido"""
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        uid = data.get('uid')
        token = data.get('token')

        # Verificar que las contraseñas coincidan
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden.'
            })

        # Verificar token y obtener usuario
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id, is_active=True)
            
            if not default_token_generator.check_token(user, token):
                raise serializers.ValidationError({
                    'token': 'El enlace de restablecimiento es inválido o ha expirado.'
                })
                
            data['user'] = user
            return data
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({
                'token': 'El enlace de restablecimiento es inválido.'
            })

    def save(self):
        """Actualizar la contraseña del usuario"""
        user = self.validated_data['user']
        password = self.validated_data['new_password']
        user.set_password(password)
        user.save()
        return user