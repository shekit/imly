from geopy import geocoders

bingeo = geocoders.Bing('AgOr3aEARXNVLGGSQe9nt2j6v9ThHyIiSNyWmoO5uw2N5RSfjt3MLBsxB_kgJTFn')

def geocode(query):
    ''' returns the first geocoded point suggested by Bing Maps '''
    for place, (lat, lng) in bingeo.geocode(query, exactly_one=False):
        return place, (lng, lat)
