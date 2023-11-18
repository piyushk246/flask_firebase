from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from firebase_admin import credentials, initialize_app, db
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize Firebase
cred = credentials.Certificate("cred.json")
initialize_app(cred, {'databaseURL': "https://mitapp-8fd20-default-rtdb.firebaseio.com/"})

# Reference to your Firebase database
ref = db.reference('/')

# Initialize empty lists for x and y data
x_data = {key: [] for key in ['voltageData', 'currentData', 'TemperatureData', 'SoCData', 'SoPData', 'SoFData', 'SoHData']}
y_data = {key: [] for key in ['voltageData', 'currentData', 'TemperatureData', 'SoCData', 'SoPData', 'SoFData', 'SoHData']}

def update_plot(value):
    print(f"Received event: Value='{value}'")
    
    try:
        for key, values in value.items():
            x_value = list(range(len(values)))
            y_value = values

            x_data[key] = x_value
            y_data[key] = y_value

            # Emit the new data to connected clients
            socketio.emit('update_plot', {'x_data': x_data, 'y_data': y_data})
            
    except (ValueError, TypeError) as e:
        print(f"Error in update_plot: {e}")
    except Exception as e:
        print(f"Error in update_plot: {e}")

def firebase_listener():
    while True:
        value = ref.get()
        if value:
            update_plot(value)
        time.sleep(5)

# Start the Firebase listener in a separate thread
firebase_thread = threading.Thread(target=firebase_listener)
firebase_thread.start()

# Routes for Flask
@app.route('/')
def index():
    return render_template('index.html')

# Start the Flask app with SocketIO support
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
    
