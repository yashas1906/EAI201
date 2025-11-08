# FINAL campus map with simple connections and TRUE ROAD DISTANCES in meters
campus_map = {
    'Main Gate': {'Admin Block': 110},
    'Admin Block': {'Main Gate': 110, 'Auditorium': 55, 'Library': 60, 'Academic Block B': 200},
    'Cafe': {'Auditorium': 40, 'Academic Block B': 150},
    'Library': {'Admin Block': 60},
    'Auditorium': {'Admin Block': 55, 'Cafe': 40, 'Academic Block B': 160},
    'Academic Block B': {'Admin Block': 200, 'Cafe': 150, 'Auditorium': 160, 'Faculty Hostel': 185},
    'Food Court': {'Faculty Hostel': 120, 'Laundry': 50, 'Sports Complex': 810},
    'Laundry': {'Food Court': 50, 'Hostel': 350},
    'Faculty Hostel': {'Academic Block B': 185, 'Food Court': 120, 'Hostel': 220},
    'Hostel': {'Faculty Hostel': 220, 'Laundry': 350, 'Sports Complex': 550},
    'Sports Complex': {
        'Hostel': 550, 'Food Court': 810, 'Football Ground': 154, 'Cricket Ground': 43, 
        'Basketball Court': 72, 'Volleyball Court': 83, 'Tennis Court': 82
    },
    'Football Ground': {'Sports Complex': 154},
    'Cricket Ground': {'Sports Complex': 43},
    'Basketball Court': {'Sports Complex': 72},
    'Volleyball Court': {'Sports Complex': 83},
    'Tennis Court': {'Sports Complex': 82},
}

# Coordinates for Chanakya University Campus
coordinates = {
    'Main Gate': (13.2213517, 77.7551040),
    'Admin Block': (13.2221039, 77.7551951),
    'Cafe': (13.2222655, 77.7551286),
    'Library': (13.2220964, 77.7554430),
    'Auditorium': (13.2222219, 77.7552483),
    'Academic Block B': (13.2232977, 77.7559360),
    'Food Court': (13.2248993, 77.7571096),
    'Laundry': (13.2245360, 77.7571372),
    'Faculty Hostel': (13.2236718, 77.7571935),
    'Hostel': (13.2244538, 77.7591013),
    'Sports Complex': (13.2281226, 77.7577549),
    'Football Ground': (13.2280384, 77.7563453),
    'Cricket Ground': (13.2284361, 77.7575469),
    'Basketball Court': (13.2287872, 77.7581721),
    'Volleyball Court': (13.2286880, 77.7585798),
    'Tennis Court': (13.2284498, 77.7583519),
}

# Information about each building for the chatbot
building_info = { 
    'Main Gate': {'Type': 'Entrance', 'Information': 'The primary entry and exit point for the campus. Security is present 24/7.', 'Timings': 'Open 24/7, but general access is restricted after 7:30 PM.'}, 
    'Admin Block': {'Type': 'Admin Building', 'Information': 'The main administrative hub. Contains offices for admissions, finance (fee payment), and the registrar.', 'Timings': '9:00 AM – 5:00 PM'}, 
    'Cafe': {'Type': 'Facility', 'Information': 'A popular spot for students to meet. Serves coffee, tea, snacks, and light meals like sandwiches and pastries.', 'Timings': '7:30 AM to 5:00 PM'}, 
    'Library': {'Type': 'Building', 'Information': 'The central library with a large collection of books and journals. Provides quiet study areas and computer access.', 'Timings': '9:00 AM to 5:00 PM'}, 
    'Auditorium': {'Type': 'Building', 'Information': 'The main hall for university events, guest lectures, seminars, and cultural performances.', 'Timings': 'Varies by event schedule. Check university announcements.'}, 
    'Academic Block B': {'Type': 'Academic Building', 'Information': 'Primarily houses the engineering departments, including classrooms, labs, and faculty offices.', 'Timings': '9:00 AM to 5:00 PM'}, 
    'Food Court': {'Type': 'Facility', 'Information': 'The main dining area for all students, especially those living in the hostel. Offers a variety of meal options.', 'Timings': '7:30 AM to 9:30 PM'}, 
    'Laundry': {'Type': 'Facility', 'Information': 'Provides laundry services for students, particularly for those in the hostel.', 'Timings': '9:30 AM to 6:00 PM'}, 
    'Faculty Hostel': {'Type': 'Residence', 'Information': 'Residential building providing accommodation for university faculty members.', 'Timings': '5:30 AM to 10:00 PM'}, 
    'Hostel': {'Type': 'Residence', 'Information': 'The main residential building for students. The in-time for residents is 10:00 PM.', 'Timings': '5:30 AM to 10:00 PM'}, 
    'Sports Complex': {'Type': 'Sports Venue', 'Information': 'The central hub for all sports facilities. Includes grounds for football and cricket, and courts for basketball, volleyball, and tennis.', 'Timings': '6:00 AM to 7:30 PM'}, 
    'Football Ground': {'Type': 'Sports Area', 'Information': 'A full-sized ground for football practice and matches.', 'Timings': '6:00 AM to 7:30 PM'}, 
    'Cricket Ground': {'Type': 'Sports Area', 'Information': 'A dedicated ground with a pitch for cricket.', 'Timings': '6:00 AM to 7:30 PM'}, 
    'Basketball Court': {'Type': 'Sports Area', 'Information': 'An outdoor court for basketball.', 'Timings': '6:00 AM to 7:30 PM'}, 
    'Volleyball Court': {'Type': 'Sports Area', 'Information': 'An outdoor court for volleyball.', 'Timings': '6:00 AM to 7:30 PM'}, 
    'Tennis Court': {'Type': 'Sports Area', 'Information': 'An outdoor court for tennis.', 'Timings': '6:00 AM to 7:30 PM'}, 
}
faq_data = { "where can I pay my fees?": "You can pay your fees at the finance office in the Admin Block.", "what are the library hours?": "The Library is open from 9:00 AM to 5:00 PM.", "what is the hostel in-time?": "The hostel in-time for residents is 10:00 PM."}