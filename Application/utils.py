
def create_request_context():
    from rest_framework.test import APIRequestFactory
    factory = APIRequestFactory()
    request = factory.get('/')
    from rest_framework.views import APIView
    request = APIView().initialize_request(request)
    context = {'request': request}
    return context
