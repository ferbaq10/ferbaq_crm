from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_superuser']
