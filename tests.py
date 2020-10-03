import unittest
from lockboxweb import functions
from datetime import datetime, timedelta
from unittest import mock
from tests.mocks import FirebaseDBMock, FirebaseDBReferenceMock


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
    def test_mock(self, mock):
        result = functions.update_boxes_to_warn()


        self.assertEqual(result['testOwner'], ['testBoxId1'])

if __name__ == "__main__":
    unittest.main()