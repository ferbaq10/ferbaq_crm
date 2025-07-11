from project.services.interfaces import AbstractProjectFactory
from project.services.project_service import ProjectService

class ProjectServiceFactory:
    def create(self) -> AbstractProjectFactory:
        return ProjectService()
