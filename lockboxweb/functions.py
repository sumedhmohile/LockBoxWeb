import os
from firebase_admin import credentials
import firebase_admin
from firebase_admin import db
import datetime
from dateutil import relativedelta, tz
from dateutil import tz


def get_start_of_plus_day(original_date, plus_days):
    if original_date is None or plus_days is None: return None
    date_start = datetime.datetime(original_date.year, original_date.month, original_date.day, tzinfo=tz.UTC)
    return date_start + datetime.timedelta(days=plus_days)


def get_start_of_plus_month(original_date, plus_months):
    return datetime.datetime(original_date.year, original_date.month, original_date.day).replace(day=1) + relativedelta.relativedelta(months=plus_months)


def get_start_of_plus_week(original_date, plus_weeks):
    return original_date - datetime.timedelta(original_date.weekday()) + datetime.timedelta(days=7)


def update_boxes_to_warn():
    reference = db.reference('boxes')
    boxes_to_warn = {}

    if reference.get():
        for user_id, user_boxes in reference.get().items():
            for box_id, box_data in user_boxes.items():
                last_checkin = int(box_data['lastCheckInDate']['time'])
                date = datetime.datetime.fromtimestamp(last_checkin // 1000)
                lock_status = box_data['lockStatus']
                if box_data['checkInFrequency'] == "Daily":
                    checkin_deadline = get_start_of_plus_day(date, 1)
                elif box_data['checkInFrequency'] == "Weekly":
                    checkin_deadline = get_start_of_plus_week(date, 1)
                else:
                    checkin_deadline = get_start_of_plus_month(date, 1)

                if checkin_deadline.timestamp() < datetime.datetime.now().timestamp() and lock_status == 'Locked':
                    if box_data['ownerId'] not in boxes_to_warn:
                        boxes_to_warn[box_data['ownerId']] = []
                    boxes_to_warn[box_data['ownerId']].append(box_data['boxId'])
                    reference.child(user_id).child(box_id).update({"lockStatus": "Warning"})

    print("Updated to warn: " + str(boxes_to_warn))

    return boxes_to_warn


cred = credentials.Certificate(os.environ['FIREBASE_CREDENTIALS_PATH'])
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ['FIREBASE_DATABASE_URL']
})