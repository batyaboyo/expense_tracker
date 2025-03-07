# app.py
from flask import Flask, render_template, request, jsonify
from simulation import Simulation

app = Flask(__name__)
simulation = Simulation()

# Initialize with some default agents
for i in range(5):
    simulation.add_agent(f"Agent {i+1}", max_workload=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_simulation():
    success = simulation.start()
    return jsonify({"success": success})

@app.route('/api/stop', methods=['POST'])
def stop_simulation():
    success = simulation.stop()
    return jsonify({"success": success})

@app.route('/api/state')
def get_state():
    return jsonify(simulation.get_state())

@app.route('/api/algorithm', methods=['POST'])
def set_algorithm():
    algorithm = request.json.get('algorithm')
    success = simulation.set_algorithm(algorithm)
    return jsonify({"success": success})

@app.route('/api/agent', methods=['POST'])
def add_agent():
    name = request.json.get('name')
    max_workload = int(request.json.get('max_workload', 1))
    agent = simulation.add_agent(name, max_workload)
    return jsonify({"success": True, "agent": agent.to_dict()})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    arrival_rate = float(request.json.get('arrival_rate', 0.2))
    min_time = int(request.json.get('min_service_time', 20))
    max_time = int(request.json.get('max_service_time', 180))
    
    success1 = simulation.set_customer_arrival_rate(arrival_rate)
    success2 = simulation.set_service_time_range(min_time, max_time)
    
    return jsonify({"success": success1 and success2})

if __name__ == '__main__':
    app.run(debug=True)
