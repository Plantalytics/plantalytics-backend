class PlantalyticsException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class PlantalyticsVineyardException(PlantalyticsException):
    pass


class PlantalyticsLoginException(PlantalyticsException):
    pass


class PlantalyticsAuthException(PlantalyticsException):
    pass
