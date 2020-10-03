class FirebaseDBReferenceMock:
    def __init__(self, reference):
        super().__init__()
        self.reference = reference
    
    def setData(self, data):
        self.data = data

    def get(self):
        return self.data

    def child(self, key):
        return self
    
    def update(self, value):
        pass
    

class FirebaseDBMock:
    def __init__(self, dbReference):
        super().__init__()
        self.reference = dbReference

    def reference(self, db):
        return self.reference


class FirebaseMessagingMock:
    def __init__(self):
        super().__init__()

    def Message(self, data, token):
        return self

    def send(self, message):
        return "DUMMY RESPONSE"

    def __str__(self):
        return "DUMMY"

