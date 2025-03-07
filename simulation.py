# simulation.py
import threading
import time
import random
from models.scheduler import Scheduler

class Simulation:
    def __init__(self):
        self.scheduler = Scheduler()
        self.running = False
        self.thread = None
        self.customer_arrival_rate = 0.2  # Average customers per second
        self.min_service_time = 20  # Minimum service time in seconds
        self.max_service_time = 180  # Maximum service time in seconds
        
    def start(self):
        """Start the simulation"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_simulation)
            self.thread.daemon = True
            self.thread.start()
            return True
        return False
    
    def stop(self):
        """Stop the simulation"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
            self.thread = None
        return True
    
    def _run_simulation(self):
        """Main simulation loop"""
        last_customer_arrival = 0
        last_update = 0
        
        while self.running:
            current_time = time.time()
            
            # Generate new customers based on arrival rate
            if current_time - last_customer_arrival > (1 / self.customer_arrival_rate):
                service_time = random.randint(self.min_service_time, self.max_service_time)
                self.scheduler.add_customer(service_time)
                last_customer_arrival = current_time
            
            # Update customer progress every cycle
            self.scheduler.update_customer_progress()
            
            # Assign new customers to agents every 5 seconds
            if current_time - last_update > 5:
                self.scheduler.assign_customers()
                last_update = current_time
                
            time.sleep(0.1)  # Prevent CPU overuse
            
    def add_agent(self, name, max_workload=1):
        """Add a new agent to the simulation"""
        return self.scheduler.add_agent(name, max_workload)
    
    def set_algorithm(self, algorithm):
        """Set the scheduling algorithm"""
        return self.scheduler.set_algorithm(algorithm)
    
    def get_state(self):
        """Get the current state of the simulation"""
        return self.scheduler.get_state()
    
    def set_customer_arrival_rate(self, rate):
        """Set the customer arrival rate"""
        if 0 < rate <= 2:  # Limit to reasonable values
            self.customer_arrival_rate = rate
            return True
        return False
    
    def set_service_time_range(self, min_time, max_time):
        """Set the service time range"""
        if 10 <= min_time < max_time <= 300:  # Reasonable limits
            self.min_service_time = min_time
            self.max_service_time = max_time
            return True
        return False
