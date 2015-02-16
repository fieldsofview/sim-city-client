import simcity, simcity.job
from simcity.job.execute import RunActor
from simcity.document import Document
import random

class MockDB(object):
    TASKS = [{'_id': 'a', 'lock': 0}, {'_id': 'b', 'lock': 0}]
    JOBS = [{'_id': 'myjob'}]
    def __init__(self):
        self.tasks = {t['_id']: t.copy() for t in MockDB.TASKS} # deep copy
        self.jobs = {t['_id']: t.copy() for t in MockDB.JOBS}
        self.saved = {}

    def get_single_from_view(self, view, **view_params):
        idx = random.choice(self.tasks.keys())
        return Document(self.tasks[idx])
    
    def get(self, idx):
        if idx in self.saved:
            return self.saved[idx]
        elif idx in self.tasks:
            return self.tasks[idx]
        elif idx in self.jobs:
            return self.jobs[idx]
        else:
            raise KeyError
    
    def save(self, doc):
        doc['_rev'] = 'something'

        if doc.id in self.jobs:
            self.jobs[doc.id] = doc.value
        else:
            if doc.id in self.tasks:
                del self.tasks[doc.id]        
            self.saved[doc.id] = doc.value
        
        return doc

class MockRun(RunActor):
    def __init__(self, callback):
        db = MockDB()
        super(MockRun, self).__init__(db)
        simcity.is_initialized = True
        simcity.job.database = db
        simcity.job.job_id = MockDB.JOBS[0]['_id']
        
        self.callback = callback
    
    def process_task(self, task):
        self.callback(task)