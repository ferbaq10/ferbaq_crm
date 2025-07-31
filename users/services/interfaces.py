from abc import ABC, abstractmethod


class AbstractUserFactory(ABC):
    @abstractmethod
    def assign_workcell(self, workcell_id: int, user):
        pass

    @abstractmethod
    def unassign_workcell(self, workcell_id: int, user):
        pass
