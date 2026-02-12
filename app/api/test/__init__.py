from flask_restx import Namespace

from app.api.test.resources.test_resource import TestResource

test_namespace = Namespace('test', path='/test')
test_namespace.add_resource(TestResource, '/',)