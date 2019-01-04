from .models import RedFlag
import datetime

red_flags = {}


class Implementation:
    def create(self, data):
        others = {
            'type': 'red-flag', 'status': 'draft', 'videos': '', 'images': ''
            }
        red_flag = RedFlag(
            (len(red_flags)+1), data['location'], data['createdBy'],
            data['comment']
            )
        red_flag.__setattr__('createdOn', datetime.datetime.now())
        for key in others:
            if key in data:
                red_flag.__setattr__(key, data[key])
            else:
                red_flag.__setattr__(key, others[key])
        red_flags[str(red_flag.id)] = red_flag.__dict__
        return [
            201, 'data', [{'id': red_flag.id, 'message': 'Created red flag'}]
            ]

    def get_flags(self):
        if not red_flags.keys():
            res = [404, 'error', 'no red flags']
        else:
            res = [200, 'data', [red_flags[key] for key in red_flags.keys()]]
        return res

    def get_flag(self, red_flag_id):
        try:
            red_flag = red_flags[str(red_flag_id)]
            res = [200, 'data', [red_flag]]
        except Exception as e:
            print(e)
            res = [404, 'error', 'red flag not found']
        return res

    def delete(self, red_flag_id):
        try:
            red_flags.pop(str(red_flag_id))
            res = [200, 'data', [{'id': int(red_flag_id), 'message':
                                 'red-flag record has been deleted'}]]
        except Exception:
            res = [404, 'error', 'red flag not found']
        return res
