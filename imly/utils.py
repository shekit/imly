from django.conf import settings
from geopy import geocoders
from keen import KeenClient
from tracking.models import Visitor
from actstream import action

tracker = KeenClient(project_id=settings.KEEN_PROJECT_ID, write_key=settings.KEEN_WRITE_KEY)
bingeo = geocoders.Bing('AvouzDHbI9nkjUD1f0pCf61BTCvTl1yHF4_TQaJQfFSxgGLNNoRm2GkGb7PGQ-ho')

def track_activity(request, **kwargs):
    actor = request.user.is_authenticated() and request.user or Visitor.objects.get(pk=request.session.pk)
    action.send(actor, **kwargs)

def geocode(query):
    ''' returns the first geocoded point suggested by Bing Maps '''
    for place, (lat, lng) in bingeo.geocode(query, exactly_one=False):
        return place, (lng, lat)

#old key - AgOr3aEARXNVLGGSQe9nt2j6v9ThHyIiSNyWmoO5uw2N5RSfjt3MLBsxB_kgJTFn