# Car emulator
Emulator of car and gps tracker devices

## Setups

### Python
Application runs using python2.7 and recommended to tun in separated virtual 
environment [virtual environment](https://virtualenv.pypa.io/)
    
    $ virtualenv car-emulator
    $ source /path/to/car-emulator/bin/activate
    
All requirements located in `requirements.txt`. To install it, run

    $ pip install -r requirements.txt

### Environment
To build paths between point application currently uses MapboxAPI. To use it, 
it's required to set MAPBOX_ACCESS_TOKEN env variable.
 
     $ export MAPBOX_ACCESS_TOKEN=[token-value]
     
You can get your personal access token 
[here](https://www.mapbox.com/help/create-api-access-token/)

### Navigation
For proper car's navigation you have to set up cities files with gps points, 
that will be used as a destination points for navigation. To do that, create 
a file `city_name.json` and fill it with gps point in GeoJSON format:
 
     [
      {
        "type": "Point",
        "coordinates": [
          30.443422,
          50.412277
        ]
      },
      ...
     ]

### Cars
To setup cars, in folder `data/` create `cars.json` file and fill if with car's 
data like this:

    [
      {
        "VIN": "101",
        "IMEI": "350000000000001",
        "city": "city_name",
        "schedule": {
          "day_start": "05:00:00",
          "day_end": "14:00:00"
        }
      }
    ]
    
Parameter `"city"` used to determine which set of point should navigator use 
for this car. It's required to have appropriate `city_name.json` file.

Parameter `"schedule"` determines working hours for car in UTC. Car will build 
route if current time lays in range `[day_start: day_end]` and finishes it's 
current route anyway.
