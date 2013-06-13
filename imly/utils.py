from django.conf import settings
from geopy import geocoders
from keen import KeenClient

tracker = KeenClient(project_id=settings.KEEN_PROJECT_ID, write_key=settings.KEEN_WRITE_KEY)
bingeo = geocoders.Bing('AgOr3aEARXNVLGGSQe9nt2j6v9ThHyIiSNyWmoO5uw2N5RSfjt3MLBsxB_kgJTFn')

def geocode(query):
    ''' returns the first geocoded point suggested by Bing Maps '''
    for place, (lat, lng) in bingeo.geocode(query, exactly_one=False):
        return place, (lng, lat)
