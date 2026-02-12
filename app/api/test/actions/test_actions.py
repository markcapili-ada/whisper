from datetime import timedelta
from sys import stderr




class TestActions:
    def hello(self, body):
       return {"message": f"Hello world from action! {body}"}