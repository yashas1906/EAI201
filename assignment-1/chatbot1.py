import sqlite3
import os

# --- Database Setup ---
def create_and_populate_db(db_path='campus_navigator.db'):
    """
    Creates and populates the SQLite database with location and timing info.
    """
    # Re-create the database to ensure it's fresh for this improved version.
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table for locations
    cursor.execute('CREATE TABLE IF NOT EXISTS locations (id INTEGER PRIMARY KEY, name TEXT UNIQUE, description TEXT, timings TEXT)')

    # Insert locations
    locations = [
        (1, 'Main Gate', 'Primary entry point', '24/7 (restricted after 7:30 pm)'),
        (2, 'Café', 'Coffee and snacks point', '7:30 am to 5 pm'),
        (3, 'Auditorium', 'Events and performances', 'Varies by event schedule'),
        (4, 'Library', 'Books and study areas', '9 am to 5 pm'),
        (5, 'Academic Block B', 'Engineering block.', '9 am to 5 pm'),
        (6, 'Food Court', 'Main dining area for hosteller students', '7:30 am to 9:30 pm'),
        (7, 'Laundry', 'Laundry services for hosteller students', '9:30 am to 6 pm'),
        (8, 'Faculty Hostel', 'Accommodation for faculty members', '5:30 am to 10 pm'),
        (9, 'Hostel', 'Student accommodation building', '5:30 am to 10 pm'),
        (10, 'Sports Complex', 'The central hub for all sports facilities', '6 am to 7:30 pm'),
        (11, 'Football Ground', 'Football play area', '6 am to 7:30 pm'),
        (12, 'Cricket Pitch', 'Cricket play area', '6 am to 7:30 pm'),
        (13, 'Basketball Court', 'Outdoor basketball court', '6 am to 7:30 pm'),
        (14, 'Volleyball Court', 'Outdoor volleyball court', '6 am to 7:30 pm'),
        (15, 'Tennis Court', 'Outdoor tennis court', '6 am to 7:30 pm'),
        (16, 'Admin Block', 'Main administrative block', '9 am to 5 pm')
    ]
    cursor.executemany('INSERT OR IGNORE INTO locations (id, name, description, timings) VALUES (?, ?, ?, ?)', locations)
    
    conn.commit()
    conn.close()
    

# --- Simple Chatbot Core ---
class BotBrain:
    def __init__(self, db_path='campus_navigator.db'):
        self.db_path = db_path
        self.locations_raw = self._load_locations_raw()
        # Create a mapping from a simplified name (lowercase, no spaces) to the original name
        self.locations_map = { self._normalize(name): name for name in self.locations_raw }

    def _load_locations_raw(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name, description, timings FROM locations')
        locations_data = {row[0]: {'description': row[1], 'timings': row[2]} for row in cursor.fetchall()}
        conn.close()
        return locations_data

    def _normalize(self, text):
        # Normalizes text for robust matching (lowercase, no spaces, handle accents)
        return text.lower().replace('é', 'e').replace(' ', '')

    def get_response(self, user_input):
        user_input_lower = user_input.lower().strip().replace('?', '')
        user_input_normalized = self._normalize(user_input_lower)

        # --- Handle Greetings and Farewells ---
        if user_input_normalized in ['hi', 'hello', 'hey']:
            return "Hello! How can I help you with campus locations or timings?"
        if user_input_normalized in ['thankyou', 'thanks']:
            return "You're welcome!"

        # --- Handle List Queries (check for exact normalized match) ---
        if user_input_normalized == 'locations':
            names = sorted(self.locations_raw.keys())
            return "Here are all the campus locations:\n- " + "\n- ".join(names)
            
        if user_input_normalized == 'timings':
            response_lines = ["Here are the timings for all campus locations:"]
            sorted_locations = sorted(self.locations_raw.items())
            for name, data in sorted_locations:
                response_lines.append(f"- {name}: {data['timings']}")
            return "\n".join(response_lines)


        if 'fees' in user_input_normalized:
            return "All fee-related payments can be made at the Admin Block."
        if 'admission' in user_input_normalized:
            return "For admissions, please visit the Admin Block."
        found_match = None
        # Sort by length to match "food court" before "food"
        for norm_name in sorted(self.locations_map.keys(), key=len, reverse=True):
            if norm_name in user_input_normalized:
                found_match = self.locations_map[norm_name]
                break
        
        if found_match:
            location_data = self.locations_raw[found_match]
            
            # Check for timing-related words in the original input
            if any(word in user_input_lower for word in ['timings', 'hours', 'open', 'close']):
                return f"The timings for the {found_match} are: {location_data['timings']}."
            # Otherwise, provide the description by default
            else:
                return f"About the {found_match}: {location_data['description']}."

        # --- Fallback Response ---
        return "I can provide information about campus locations and their timings. Please ask about a specific place or use keywords."

# --- Main Application Loop ---
if __name__ == '__main__':
    create_and_populate_db()
    bot = BotBrain()
    print("BotBrain Campus Information Bot Initialized.")
    print("Ask about locations and timings, or type 'quit' to exit.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("You: ")
            # CRITICAL FIX: Check for empty input to prevent crashes
            if not user_input.strip():
                continue
            
            if user_input.lower().strip() in ['quit', 'exit', 'bye']:
                print("BotBrain: Goodbye!")
                break
                
            response = bot.get_response(user_input)
            print(f"BotBrain: {response}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nBotBrain: Goodbye!")
            break
