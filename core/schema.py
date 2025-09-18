import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from graphql import GraphQLError

from project.models import Project
from catalog.models import ProjectStatus, Specialty, Subdivision, WorkCell
from project.services.project_service import ProjectService


# Tipos GraphQL
class ProjectStatusType(DjangoObjectType):
    class Meta:
        model = ProjectStatus
        fields = "__all__"


class SpecialtyType(DjangoObjectType):
    class Meta:
        model = Specialty
        fields = "__all__"


class SubdivisionType(DjangoObjectType):
    division_name = graphene.String()

    class Meta:
        model = Subdivision
        fields = "__all__"

    def resolve_division_name(self, info):
        return self.division.name if self.division else None


class WorkCellType(DjangoObjectType):
    udn_name = graphene.String()

    class Meta:
        model = WorkCell
        fields = "__all__"

    def resolve_udn_name(self, info):
        return self.udn.name if self.udn else None


class ProjectType(DjangoObjectType):
    can_edit = graphene.Boolean()
    can_delete = graphene.Boolean()

    class Meta:
        model = Project
        fields = "__all__"

    def resolve_can_edit(self, info):
        """Verificar si el usuario puede editar este proyecto"""
        user = info.context.user
        if not user.is_authenticated:
            return False
        return user.has_perm('project.change_project')

    def resolve_can_delete(self, info):
        """Verificar si el usuario puede eliminar este proyecto"""
        user = info.context.user
        if not user.is_authenticated:
            return False
        return user.has_perm('project.delete_project')


# Queries
class Query(graphene.ObjectType):
    # Consultas de proyectos
    all_projects = graphene.List(ProjectType)
    project_by_id = graphene.Field(ProjectType, id=graphene.Int(required=True))
    my_projects = graphene.List(ProjectType)

    # Consultas de catálogos
    all_project_statuses = graphene.List(ProjectStatusType)
    all_specialties = graphene.List(SpecialtyType)
    all_subdivisions = graphene.List(SubdivisionType)
    all_work_cells = graphene.List(WorkCellType)

    @login_required
    def resolve_all_projects(self, info):
        """Obtener todos los proyectos según permisos del usuario"""
        user = info.context.user

        if not user.has_perm('project.view_project'):
            raise GraphQLError("Permission denied: view_project required")

        service = ProjectService()
        return service.get_base_queryset(user)

    @login_required
    def resolve_project_by_id(self, info, id):
        """Obtener proyecto por ID"""
        user = info.context.user

        if not user.has_perm('project.view_project'):
            raise GraphQLError("Permission denied: view_project required")

        try:
            service = ProjectService()
            queryset = service.get_base_queryset(user)
            return queryset.get(id=id)
        except Project.DoesNotExist:
            return None

    @login_required
    def resolve_my_projects(self, info):
        """Obtener proyectos del usuario actual"""
        user = info.context.user
        service = ProjectService()
        queryset = service.get_base_queryset(user)

        # Filtrar por proyectos donde el usuario esté en work_cell
        return queryset.filter(work_cell__users=user)

    @login_required
    def resolve_all_project_statuses(self, info):
        """Obtener todos los estados de proyecto activos"""
        return ProjectStatus.objects.filter(is_active=True)

    @login_required
    def resolve_all_specialties(self, info):
        """Obtener todas las especialidades activas"""
        return Specialty.objects.filter(is_active=True)

    @login_required
    def resolve_all_subdivisions(self, info):
        """Obtener todas las subdivisiones activas"""
        return Subdivision.objects.select_related('division').filter(is_active=True)

    @login_required
    def resolve_all_work_cells(self, info):
        """Obtener todas las células de trabajo activas"""
        return WorkCell.objects.select_related('udn').filter(is_active=True)


# Mutations
class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        latitude = graphene.Float()
        longitude = graphene.Float()
        project_status_id = graphene.Int(required=True)
        specialty_id = graphene.Int()
        subdivision_id = graphene.Int(required=True)
        work_cell_id = graphene.Int(required=True)

    project = graphene.Field(ProjectType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, name, project_status_id, subdivision_id, work_cell_id, **kwargs):
        user = info.context.user

        if not user.has_perm('project.add_project'):
            return CreateProject(
                project=None,
                success=False,
                errors=["Permission denied: add_project required"]
            )

        try:
            # Validar que existan las relaciones
            project_status = ProjectStatus.objects.get(id=project_status_id, is_active=True)
            subdivision = Subdivision.objects.get(id=subdivision_id, is_active=True)
            work_cell = WorkCell.objects.get(id=work_cell_id, is_active=True)

            specialty = None
            if kwargs.get('specialty_id'):
                specialty = Specialty.objects.get(id=kwargs['specialty_id'], is_active=True)

            # Crear el proyecto
            project_data = {
                'name': name,
                'description': kwargs.get('description', ''),
                'latitude': kwargs.get('latitude'),
                'longitude': kwargs.get('longitude'),
                'project_status': project_status_id,
                'specialty': kwargs.get('specialty_id'),
                'subdivision': subdivision_id,
                'work_cell': work_cell_id,
            }

            service = ProjectService()
            project = service.create(project_data)

            return CreateProject(project=project, success=True, errors=[])

        except (ProjectStatus.DoesNotExist, Subdivision.DoesNotExist,
                WorkCell.DoesNotExist, Specialty.DoesNotExist) as e:
            return CreateProject(
                project=None,
                success=False,
                errors=[f"Related object not found: {str(e)}"]
            )
        except Exception as e:
            return CreateProject(
                project=None,
                success=False,
                errors=[str(e)]
            )


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        description = graphene.String()
        latitude = graphene.Float()
        longitude = graphene.Float()
        project_status_id = graphene.Int()
        specialty_id = graphene.Int()
        subdivision_id = graphene.Int()
        work_cell_id = graphene.Int()

    project = graphene.Field(ProjectType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, id, **kwargs):
        user = info.context.user

        if not user.has_perm('project.change_project'):
            return UpdateProject(
                project=None,
                success=False,
                errors=["Permission denied: change_project required"]
            )

        try:
            service = ProjectService()
            queryset = service.get_base_queryset(user)
            project = queryset.get(id=id)

            # Preparar datos para actualizar
            update_data = {}
            for field, value in kwargs.items():
                if value is not None:
                    update_data[field] = value

            updated_project = service.update(project, update_data)

            return UpdateProject(project=updated_project, success=True, errors=[])

        except Project.DoesNotExist:
            return UpdateProject(
                project=None,
                success=False,
                errors=["Project not found"]
            )
        except Exception as e:
            return UpdateProject(
                project=None,
                success=False,
                errors=[str(e)]
            )


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, id):
        user = info.context.user

        if not user.has_perm('project.delete_project'):
            return DeleteProject(
                success=False,
                errors=["Permission denied: delete_project required"]
            )

        try:
            service = ProjectService()
            queryset = service.get_base_queryset(user)
            project = queryset.get(id=id)

            # Soft delete usando is_removed
            project.is_removed = True
            project.save()

            return DeleteProject(success=True, errors=[])

        except Project.DoesNotExist:
            return DeleteProject(
                success=False,
                errors=["Project not found"]
            )
        except Exception as e:
            return DeleteProject(
                success=False,
                errors=[str(e)]
            )


class ToggleProjectState(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        is_removed = graphene.Boolean(required=True)

    project = graphene.Field(ProjectType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, id, is_removed):
        user = info.context.user

        if not user.has_perm('project.change_project'):
            return ToggleProjectState(
                project=None,
                success=False,
                errors=["Permission denied: change_project required"]
            )

        try:
            service = ProjectService()
            queryset = service.get_base_queryset(user)
            project = queryset.get(id=id)

            project.is_removed = is_removed
            project.save()

            return ToggleProjectState(project=project, success=True, errors=[])

        except Project.DoesNotExist:
            return ToggleProjectState(
                project=None,
                success=False,
                errors=["Project not found"]
            )


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()
    toggle_project_state = ToggleProjectState.Field()


# Schema principal
schema = graphene.Schema(query=Query, mutation=Mutation)