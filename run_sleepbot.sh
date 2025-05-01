#!/bin/bash

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate sleepbot

# Run Flask app in background and open browser
echo "Launching SleepBot (Flask)..."
python flask_app.py &

# Wait briefly and open in browser
sleep 2
python -m webbrowser http://127.0.0.1:5050