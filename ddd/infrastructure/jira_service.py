from ddd.domain.employee import Employee
from ddd.domain.report import Report


class JIRAService:
    def get_tickets(self, tickets, employee: Employee) -> list[Report]:
        # pull from server
        # parse into Report objects
        # return list of Report objects
        pass