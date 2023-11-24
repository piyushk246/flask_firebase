from flask import Flask, render_template
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
import base64
from firebase_admin import credentials, initialize_app, db
import threading
import time
import schedule
import matplotlib.pyplot as plt
import select

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("cred.json")
initialize_app(cred, {'databaseURL': "https://mitapp-8fd20-default-rtdb.firebaseio.com/"})

# Reference to your Firebase database
ref = db.reference('/')

# Define the order and custom labels for the graphs
parameter_order = ['voltageData', 'currentData', 'TemperatureData', 'SoCData', 'SoFData', 'SoHData', 'SoPData']
parameter_labels = {'voltageData': 'Voltage', 'currentData': 'Current', 'TemperatureData': 'Temperature',
                    'SoCData': 'SoC', 'SoFData': 'SoF', 'SoHData': 'SoH', 'SoPData': 'SoP'}

# Initialize empty lists for x and y data
data = {key: {'x': [], 'y': []} for key in parameter_order}

# Create a Matplotlib Figure and Axes for each parameter
fig, axs = plt.subplots(len(data), 1, figsize=(8, 6), dpi=100, sharex=True)
fig.subplots_adjust(hspace=0.5)

# Create a FigureCanvasAgg to render the figure
canvas = FigureCanvasAgg(fig)

def update_plot():
    try:
        value = ref.get()
        for i, key in enumerate(parameter_order):
            values = value.get(key, [])  # Use get() to handle missing keys gracefully
            x_value = list(range(len(values)))
            y_value = values

            data[key]['x'] = x_value
            data[key]['y'] = y_value

            # Clear the existing plot and redraw it with new data
            axs[i].clear()
            axs[i].plot(data[key]['x'], data[key]['y'])
            axs[i].set_title(parameter_labels[key])

        # Draw the figure on the canvas
        canvas.draw()
    except (ValueError, TypeError) as e:
        print(f"Error in update_plot: {e}")
    except Exception as e:
        print(f"Error in update_plot: {e}")

def job():
    with app.app_context():
        update_plot()

# Schedule the job to run every 5 seconds
schedule.every(5).seconds.do(job)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the schedule in a separate thread
schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()

@app.route('/')
def index():
    # Convert the plot to a PNG image
    output = io.BytesIO()
    canvas.print_png(output)
    img_data = base64.b64encode(output.getvalue()).decode('utf-8')

    print("Rendering template")
    return render_template('index.html', img_data=img_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
