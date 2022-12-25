
class PatientException(Exception):
    def __init__(self, external_id: int, message="Patient error"):
        self.external_id = external_id
        self.message = message
        super().__init__(self.message)


class PatientNotFoundException(PatientException):
    def __init__(self, external_id: int):
        super().__init__(external_id=external_id, message="Patient {0} is not found".format(external_id))


class PatientAlreadyExistsException(PatientException):
    def __init__(self, external_id: int):
        super().__init__(external_id=external_id, message="Patient {0} already exists".format(external_id))
