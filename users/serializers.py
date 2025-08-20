from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError

from .models import UserProfile

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Personaliza el payload del token
        token['user_id'] = user.id
        token['username'] = user.username

        token['roles'] = list(user.groups.values_list('name', flat=True))

        # Añadir permisos como lista de codenames
        token['permissions'] = cls.get_permissions(user)
        token['workCells'] = [
            {
                'id': wc.id,
                'name': wc.name,
            }
            for wc in user.workcell.all()
        ]

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
            
            # ✅ DEBUG: Ver qué está generando
            print(f"🔍 SharePoint URL: {obj.photo_sharepoint_url}")
            print(f"🔍 Filename extraído: {filename}")
            print(f"🔍 Proxy URL generada: {proxy_url}")
            
            return proxy_url
        return None


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'profile']


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