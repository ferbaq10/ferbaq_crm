from users.services.interfaces import AbstractUserFactory
from users.services.user_service import UserService

class UserServiceFactory:
    def create(self) -> AbstractUserFactory:
        return UserService()
