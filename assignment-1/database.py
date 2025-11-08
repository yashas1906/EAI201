# Campus map represented as a graph with distances in meters
campus_map = {
    'Main Gate': {'Admin Block': 90, 'Cafe': 152, 'Library': 105},
    'Admin Block': {'Main Gate': 90, 'Auditorium': 12, 'Library': 12, 'Academic Block B': 115, 'Connecting Point': 103},
    'Cafe': {'Main Gate': 152, 'Auditorium': 12, 'Academic Block B': 148},
    'Library': {'Main Gate': 105, 'Admin Block': 12, 'Hostel': 635},
    'Auditorium': {'Admin Block': 12, 'Cafe': 12},
    'Academic Block B': {'Admin Block': 115, 'Cafe': 148, 'Food Court': 183, 'Faculty Hostel': 165},
    'Connecting Point': {'Admin Block': 103},
    'Food Court': {'Academic Block B': 183, 'Laundry': 105, 'Sports Complex': 667},
    'Laundry': {'Food Court': 105, 'Faculty Hostel': 82, 'Hostel': 268},
    'Faculty Hostel': {'Academic Block B': 165, 'Laundry': 82, 'Hostel': 280},
    'Hostel': {'Library': 635, 'Laundry': 268, 'Faculty Hostel': 280, 'Sports Complex': 590},
    'Sports Complex': {'Food Court': 667, 'Hostel': 590, 'Football Ground': 154, 'Cricket Ground': 43, 'Basketball Court': 72, 'Volleyball Court': 83, 'Tennis Court': 82},
    'Football Ground': {'Sports Complex': 154},
    'Cricket Ground': {'Sports Complex': 43},
    'Basketball Court': {'Sports Complex': 72},
    'Volleyball Court': {'Sports Complex': 83},
    'Tennis Court': {'Sports Complex': 82},
}

# Coordinates for A* heuristic (approximated for demonstration)
coordinates = {
    'Main Gate': (5, 0),
    'Admin Block': (5, 2),
    'Cafe': (3, 3),
    'Library': (7, 2),
    'Auditorium': (5, 3),
    'Academic Block B': (5, 5),
    'Connecting Point': (6, 4),
    'Food Court': (5, 8),
    'Laundry': (6, 9),
    'Faculty Hostel': (7, 7),
    'Hostel': (9, 9),
    'Sports Complex': (8, 12),
    'Football Ground': (7, 13),
    'Cricket Ground': (9, 13),
    'Basketball Court': (7, 14),
    'Volleyball Court': (8, 14),
    'Tennis Court': (9, 14),
}

# Information about each building
building_info = {
    'Main Gate': {'Type': 'Entrance', 'Information': 'The primary entry and exit point for the campus.', 'Timings': '24/7 (restricted access after 7:30 pm)'},
    'Admin Block': {'Type': 'Admin Building', 'Information': 'The main administrative block of the college regarding, enquires ,admissions ,finances etc', 'Timings': '9 am – 5 pm'},
    'Cafe': {'Type': 'Facility', 'Information': 'Serves coffee, snacks, and light meals. A common student meeting point.', 'Timings': '7:30 am to 5 pm'},
    'Library': {'Type': 'Building', 'Information': 'Contains the main collection of books, journals, and provides quiet study areas.', 'Timings': '9 am to 5 pm'},
    'Auditorium': {'Type': 'Building', 'Information': 'Main hall for university events, seminars, and performances.', 'Timings': 'Varies by event schedule'},
    'Academic Block B': {'Type': 'Academic Building', 'Information': 'Engineering block.', 'Timings': '9 am to 5 pm'},
    'Food Court': {'Type': 'Facility', 'Information': 'The main dining area for hosteller students.', 'Timings': '7:30 am to 9:30 pm'},
    'Laundry': {'Type': 'Facility', 'Information': 'Laundry services for hosteller students', 'Timings': '9:30 am to 6 pm'},
    'Faculty Hostel': {'Type': 'Residence', 'Information': 'Accommodation facilities designated for university faculty members.', 'Timings': '5:30 am to 10 pm'},
    'Hostel': {'Type': 'Residence', 'Information': 'The main accommodation and residential building for students.', 'Timings': '5:30 am to 10 pm'},
    'Sports Complex': {'Type': 'Sports Venue', 'Information': 'The central hub for all sports facilities', 'Timings': '6 am to 7:30 pm'},
    'Football Ground': {'Type': 'Sports Area', 'Information': 'Football play area for practice,matches etc.', 'Timings': '6 am to 7:30 pm'},
    'Cricket Ground': {'Type': 'Sports Area', 'Information': 'Cricket play area for practice,matches etc', 'Timings': '6 am to 7:30 pm'},
    'Basketball Court': {'Type': 'Sports Area', 'Information': 'Outdoor court for basketball games and practice', 'Timings': '6 am to 7:30 pm'},
    'Volleyball Court': {'Type': 'Sports Area', 'Information': 'Outdoor court fro volleyball games and practice', 'Timings': '6 am to 7:30 pm'},
    'Tennis Court': {'Type': 'Sports Area', 'Information': 'Outdoor court for tennis matches and practice', 'Timings': '6 am to 7:30 pm'},
}

# Frequently Asked Questions for the chatbot
faq_data = {
    "what are the library hours?": "The Library is open from 9 am to 5 pm.",
    "when does the cafe close?": "The Cafe closes at 5 pm.",
    "what are the timings for the sports complex?": "The Sports Complex is open from 6 am to 7:30 pm.",
    "when is the food court open?": "The Food Court is open from 7:30 am to 9:30 pm.",
    "what time does the admin block open?": "The Admin Block opens at 9 am.",
    "what is the hostel in-time?": "The hostel in-time is 10 pm.",
    "when can i use the laundry services?": "Laundry services are available from 9:30 am to 6 pm.",
    "where can i pay my fees?": "You can pay your fees at the Admin Block.",
    "what is in academic block b?": "Academic Block B is the Engineering block.",
    "how do i use the navigator?": "Simply enter your starting location and destination, then choose a search algorithm to find the best path.",
    "how do i connect to the campus wi-fi?": "You can connect to the campus Wi-Fi using your student credentials. For help, please visit the IT department in the Admin Block.",
    "what are the admission hours?": "For admissions, please visit the Admin Block between 9 am to 5 pm.",
    "where is the main gate located?": "The Main Gate is the primary entry and exit point for the campus, located at the front of the university.",
    "what sports facilities are available?": "The Sports Complex includes facilities for football, cricket, basketball, volleyball, and tennis.",
    "where can i find the auditorium?": "The Auditorium is located near the Admin Block and is used for university events and performances.",
    "where can i do admissions?": "Admissions are handled at the Admin Block.",
    "admission": "For admissions, please visit the Admin Block.",
    "fees": "All fee-related payments can be made at the Admin Block.",
    "laundry": "Laundry services for hosteller students are available from 9:30 am to 6 pm.",
    "main gate timings": "The Main Gate is accessible 24/7, but access is restricted after 7:30 pm."
}

