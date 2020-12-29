import unittest
from lockboxweb import functions
from datetime import datetime, timedelta
from unittest import mock
from tests.mocks import FirebaseDBMock, FirebaseDBReferenceMock, FirebaseMessagingMock


def getFireBaseDBMockForWarnUpdate(*args, **kwargs):
    test_box_data = {}

    test_box_data['dummyId'] = {}
    test_box_data['dummyId']['dummyBox1'] = {}
    test_box_data['dummyId']['dummyBox1']['lastCheckInDate'] = {'time': (datetime.now() + timedelta(days=-3)).timestamp()}
    test_box_data['dummyId']['dummyBox1']['checkInFrequency'] = 'Daily'
    test_box_data['dummyId']['dummyBox1']['ownerId'] = 'testOwner'
    test_box_data['dummyId']['dummyBox1']['lockStatus'] = 'Locked'
    test_box_data['dummyId']['dummyBox1']['boxId'] = 'testBoxId1'

    test_box_data['dummyId']['dummyBox2'] = {}
    test_box_data['dummyId']['dummyBox2']['lastCheckInDate'] = {'time': (datetime.now() + timedelta(days=1)).timestamp()}
    test_box_data['dummyId']['dummyBox2']['checkInFrequency'] = 'Daily'
    test_box_data['dummyId']['dummyBox2']['ownerId'] = 'testOwner'
    test_box_data['dummyId']['dummyBox2']['lockStatus'] = 'Unlocked'
    test_box_data['dummyId']['dummyBox2']['boxId'] = 'testBoxId2'

    referenceMock = FirebaseDBReferenceMock('test')
    referenceMock.setData(test_box_data)

    return referenceMock

def getFireBaseDBMockForUnlockUpdate(*args, **kwargs):
    test_box_data = {}

    test_box_data['dummyId'] = {}
    test_box_data['dummyId']['dummyBox1'] = {}
    test_box_data['dummyId']['dummyBox1']['lastCheckInDate'] = {'time': (datetime.now() + timedelta(days=-3)).timestamp()}
    test_box_data['dummyId']['dummyBox1']['checkInFrequency'] = 'Daily'
    test_box_data['dummyId']['dummyBox1']['ownerId'] = 'testOwner'
    test_box_data['dummyId']['dummyBox1']['lockStatus'] = 'Warning'
    test_box_data['dummyId']['dummyBox1']['boxId'] = 'testBoxId1'
    test_box_data['dummyId']['dummyBox1']['name'] = 'Test Box 1'

    test_box_data['dummyId']['dummyBox2'] = {}
    test_box_data['dummyId']['dummyBox2']['lastCheckInDate'] = {'time': (datetime.now() + timedelta(days=1)).timestamp()}
    test_box_data['dummyId']['dummyBox2']['checkInFrequency'] = 'Daily'
    test_box_data['dummyId']['dummyBox2']['ownerId'] = 'testOwner'
    test_box_data['dummyId']['dummyBox2']['lockStatus'] = 'Locked'
    test_box_data['dummyId']['dummyBox2']['boxId'] = 'testBoxId2'
    test_box_data['dummyId']['dummyBox2']['name'] = 'Test Box 2'

    referenceMock = FirebaseDBReferenceMock('test')
    referenceMock.setData(test_box_data)

    return referenceMock


def getFireBaseMessagingMock(*args, **kwargs):
    return FirebaseMessagingMock()

def getFireBaseMessagingMockSendResponse(*args, **kwargs):
    return FirebaseMessagingMock().send("test")

class Tests(unittest.TestCase):
    def setUp(self):
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def test_get_start_of_plus_day(self):
        start_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
        end_date = '2020-01-02'
        add_days = 1

        result = functions.get_start_of_plus_day(start_date, add_days).strftime('%Y-%m-%d')
        self.assertEqual(end_date, result)

        end_date = '2020-01-01'
        add_days = 0
        result = functions.get_start_of_plus_day(start_date, add_days).strftime('%Y-%m-%d')
        self.assertEqual(end_date, result)

        result = functions.get_start_of_plus_day(start_date, None)
        self.assertEqual(None, result)

        result = functions.get_start_of_plus_day(None, None)
        self.assertEqual(None, result)

        result = functions.get_start_of_plus_day(None, 1)
        self.assertEqual(None, result)


    @mock.patch('firebase_admin.db.reference', side_effect=getFireBaseDBMockForWarnUpdate)
    def test_update_boxes_to_warn(self, mock):
        result = functions.update_boxes_to_warn()
        self.assertEqual(result['testOwner'], ['testBoxId1'])


    @mock.patch('firebase_admin.db.reference', side_effect=getFireBaseDBMockForUnlockUpdate)
    @mock.patch('firebase_admin.messaging.Message', side_effect=getFireBaseMessagingMock)
    @mock.patch('firebase_admin.messaging.send', side_effect=getFireBaseMessagingMockSendResponse)
    def test_update_boxes_to_unlock(self, dbMock, messageMock, sendMock):
        result = functions.update_boxes_to_unlock()
        self.assertEqual(result['testOwner'], ['Test Box 1'])


    @mock.patch('firebase_admin.messaging.Message', side_effect=getFireBaseMessagingMock)
    @mock.patch('firebase_admin.messaging.send', side_effect=getFireBaseMessagingMockSendResponse)
    def test_send_message_to_token(self, messageMock, sendMock):
        result = functions.send_message_to_token("test_id", "test_command", "test_message", "test_token")
        self.assertEqual(result, "DUMMY RESPONSE")

if __name__ == "__main__":
    unittest.main()