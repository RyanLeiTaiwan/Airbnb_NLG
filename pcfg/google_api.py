import googlemaps

# api: Google API client object
# lat: latitude
# lng: longitude
# attactions: list of attractions
# max_walk: maximum acceptable walking time in minutes
def distance_attractions(api, lat, lng, city, attractions, max_walk):
	# Empty attractions
	if len(attractions) == 0:
		return ''

	min_time = float('+inf')
	max_time = float('-inf')
	try:
		origins = str(lat) + ',' + str(lng)
		destinations = ''
		# Use Geocode API to get the (lat, lng) of each attraction (stored in destinations)
		for att in attractions:
			geocode = api.geocode(att + ', ' + city)[0]
			loc = geocode['geometry']['location']
			destinations += str(loc['lat']) + ',' + str(loc['lng']) + '|'

		# Use Distance Matrix API to compute travel time from property to all attractions
		dist_walk = api.distance_matrix(origins=origins, destinations=destinations, mode='walking')
		for element in dist_walk['rows'][0]['elements']:
			minute = round(element['duration']['value'] / 60.0)
			if minute < min_time:
				min_time = minute
			if minute > max_time:
				max_time = minute
		if max_time <= max_walk:
			if min_time == max_time:
				return 'A %d-minute walk' % max_time
			else:
				return 'A %d-to-%d-minute walk' % (min_time, max_time)
		else:
			# It is too long to walk, return the driving time instead
			min_time = float('+inf')
			max_time = float('-inf')
			dist_drive = api.distance_matrix(origins=origins, destinations=destinations, mode='driving')
			for element in dist_drive['rows'][0]['elements']:
				minute = round(element['duration']['value'] / 60.0)
				if minute < min_time:
					min_time = minute
				if minute > max_time:
					max_time = minute
			if min_time == max_time:
				return 'A %d-minute drive' % max_time
			else:
				return 'A %d-to-%d-minute drive' % (min_time, max_time)
	except:
		return 'unknown distance'

if __name__ == '__main__':
	apikey = 'AIzaSyDpC11dt2AcHTva0XhKhwC3J0kvVJIGdkM'
	api = googlemaps.Client(key=apikey)
	lat = 42.28451220982457
	lng = -71.1362580468337
	city = 'Boston'
	attractions = ['roslindale village', 'roslindale square', 'the arnold arboretum', 'emerald necklace']
	# att = ['jp, the arnold arboretum, jamaica, jamaica pond']
	# att = ['the museum of fine arts', 'longwood', 'northeastern university', 'penguin pizza']
	print distance_attractions(api, lat, lng, city, attractions, max_walk=30)
