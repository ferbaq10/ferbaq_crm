from django.db import migrations

def create_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Modelos del mismo módulo
    model_names = [
        'Contact'
    ]

    # Crear grupos
    roles = {
        'Director Comercial': [],
        'Gerente Comercial': [],
        'Vendedor': [],
        'Comprador': [],
    }

    for role_name in roles.keys():
        group, _ = Group.objects.get_or_create(name=role_name)
        roles[role_name] = group

    # Crear permisos y asignarlos a los grupos
    for model_name in model_names:
        ct = ContentType.objects.get(app_label='contact', model=model_name.lower())

        perms = Permission.objects.filter(content_type=ct)

        for perm in perms:
            # Director: todos los permisos
            roles['Director Comercial'].permissions.add(perm)

            # Gerente Comercial: ver, agregar y cambiar
            if perm.codename.startswith(('view_', 'add_', 'change_')):
                roles['Gerente Comercial'].permissions.add(perm)

            # Vendedor: solo ver
            if perm.codename.startswith('view_'):
                roles['Vendedor'].permissions.add(perm)

            # Comprador: sin permisos en estos modelos

def remove_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    group_names = ['Director Comercial', 'Gerente Comercial', 'Vendedor', 'Comprador']
    Group.objects.filter(name__in=group_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions, remove_roles_and_permissions),
    ]
