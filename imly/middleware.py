class RefererMiddleware(object):
    ''' middleware to setup referer in requests to '''
    def process_request(self, request):
        try:
            request.referer = request.META['HTTP_REFERER']
        except KeyError:
            request.referer = request.session.get('referer', '/food/')
            request.session['referer'] = request.path
