from .models import RedFlag
import datetime
from app.implementation import Implementation


class Validation:
    data_types = {
        'id': int,
        'createdOn': datetime.datetime,
        'createdBy': int,
        'type': str,
        'location': str,
        'status': str,
        'Images': str,
        'Videos': str,
        'comment': str
        }

    def bad_type(self, data):
        for field in data:
            if field in self.data_types and not isinstance(
                    data[field], self.data_types[field]):
                return [
                    400, 'error',
                    f'{field} should be of type {self.data_types[field]}'
                    ]
            # check forinvalid keys in data
            elif field not in self.data_types:
                return [400, 'error', f'unknown input {field}']

    def validateNew(self, data):
        for field in ['location', 'comment', 'createdBy']:
            if field not in data:
                return [
                    400, 'error',
                    f'{field} field missing, invalid key or incorrect'
                    ]
            elif not data[field]:
                return [400, 'error', 'please submit {}'.format(field)]
        if self.bad_type(data):
            result = self.bad_type(data)
        else:
            result = Implementation().create(data)
        return result
