# Academic Digital Twin

The Academic Digital Twin is an AI-powered Flask app that simulates a student's academic semester. You enter your GPA, courses, stress levels, sleep, work hours, and other factors, and it predicts where you'll end up, how likely you are to burn out, and how much academic risk you're carrying.
The model actually learns over time. Every submission gets saved to a dataset and the model retrains automatically, so the more students use it the smarter it gets. There's also a Claude-powered chat advisor built in that can answer questions about your results and give personalized advice based on your profile.

## Features

- Academic risk prediction
- GPA trajectory simulation
- Burnout probability estimation
- Scenario-based recommendations

## Tech Stack

- Python
- Flask
- HTML / CSS
- Jinja Templates

## ChatBot Instructions
1. Copy .env.example to .env
2. Add your Anthropic API key at console.anthropic.com
3. pip install -r requirements.txt
4. python app.py

##Installation

- VSCode

python3 app.py

http://127.0.0.1:5001
