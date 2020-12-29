import os
from firebase_admin import credentials
import firebase_admin
from firebase_admin import db, messaging
import datetime
from dateutil import relativedelta, tz
from dateutil import tz


def send_message_to_token(notification_id, command, message, token):
    registration_token = token

    message = messaging.Message(
        data={
            "message":message,
            "notification_type":command,
            "notification_id":notification_id
        },
        token=registration_token,
    )

    response = messaging.send(message)

    print('Successfully sent message:' + str(response) + "to token " + token)

    return response
    

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

    user_reference = db.reference("users")

    if user_reference.get():
        for user_id, user_data in user_reference.get().items():
            if user_id in boxes_to_warn.keys():
                message = "You have " + str(len(boxes_to_warn[user_id])) + " boxes pending"
                send_message_to_token("1", "NOTIFICATION_WARN", message, user_data['fcmToken'])

    return boxes_to_warn


def update_boxes_to_unlock():
    reference = db.reference('boxes')
    boxes = []
    boxes_to_unlock = {}

    if reference.get():
        for user_id, user_boxes in reference.get().items():
            for box_id, box_data in user_boxes.items():
                last_checkin = int(box_data['lastCheckInDate']['time'])
                lock_status = box_data['lockStatus']
                date = datetime.datetime.fromtimestamp(last_checkin // 1000)
                if box_data['checkInFrequency'] == "Daily":
                    checkin_deadline = get_start_of_plus_day(date, 2)
                elif box_data['checkInFrequency'] == "Weekly":
                    checkin_deadline = get_start_of_plus_week(date, 2)
                else:
                    checkin_deadline = get_start_of_plus_month(date, 2)

                if checkin_deadline.timestamp() < datetime.datetime.now().timestamp() and lock_status == 'Warning':
                    boxes.append(box_data['boxId'])
                    if box_data['ownerId'] not in boxes_to_unlock:
                        boxes_to_unlock[box_data['ownerId']] = []
                    boxes_to_unlock[box_data['ownerId']].append(box_data['name'])
                    reference.child(user_id).child(box_id).update({"lockStatus": "Unlocked"})

    print("Updated to unlock: " + str(boxes_to_unlock))

    user_reference = db.reference("users")

    if user_reference.get():
        for user_id, user_data in user_reference.get().items():
            if user_id in boxes_to_unlock.keys():
                message = "Box: " + ''.join(boxes_to_unlock[user_id]) + " has been unlocked."
                if len(boxes_to_unlock[user_id]) > 1:
                    box_list = boxes_to_unlock[user_id]
                    message = "Boxes " + ', '.join(box_list[0: len(box_list) - 1]) + " and " + box_list[len(box_list) - 1] + " have been unlocked."
                send_message_to_token("2", "NOTIFICATION_UNLOCKED", message, user_data['fcmToken'])


    return boxes_to_unlock

cred = credentials.Certificate(os.environ['FIREBASE_CREDENTIALS_PATH'])
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ['FIREBASE_DATABASE_URL']
})