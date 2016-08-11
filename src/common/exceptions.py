class PlantalyticsException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class PlantalyticsAuthException(PlantalyticsException):
    pass


class PlantalyticsDataException(PlantalyticsException):
    pass


class PlantalyticsEmailException(PlantalyticsException):
    pass


class PlantalyticsHubException(PlantalyticsException):
    pass


class PlantalyticsLoginException(PlantalyticsException):
    pass


class PlantalyticsPasswordException(PlantalyticsException):
    pass


class PlantalyticsVineyardException(PlantalyticsException):
    pass
