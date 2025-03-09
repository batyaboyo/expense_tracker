import random
import time
import threading
from models import Customer, Agent, Scheduler

class Simulation:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.running = False
        self.simulation_thread = None
        self.customer_generation_thread = None
        self.customer_completion_thread = None
        
    def start(self):
        if self.running:
            return
            
        self.running = True
        
        # Initialize agents if not already done
        if not self.scheduler.agents:
            agent_names = ["Aketch", "Batya", "Muhanguzi"]
            for i, name in enumerate(agent_names[:3]):
                self.scheduler.add_agent(Agent(name, max_workload=3))
        
        # Start customer generation thread
        self.customer_generation_thread = threading.Thread(target=self._generate_customers)
        self.customer_generation_thread.daemon = True
        self.customer_generation_thread.start()
        
        # Start customer completion thread
        self.customer_completion_thread = threading.Thread(target=self._process_customer_completions)
        self.customer_completion_thread.daemon = True
        self.customer_completion_thread.start()
        
        # Start main simulation thread
        self.simulation_thread = threading.Thread(target=self._run_simulation)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
    def stop(self):
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)
        if self.customer_generation_thread:
            self.customer_generation_thread.join(timeout=1.0)
        if self.customer_completion_thread:
            self.customer_completion_thread.join(timeout=1.0)
    
    def _generate_customers(self):
        """Generate new customers at random intervals"""
        while self.running:
            # Random wait between 1-5 seconds before generating a new customer
            wait_time = random.uniform(1, 5)
            time.sleep(wait_time)
            
            # Generate a new customer with random service time and priority
            service_time = random.randint(5, 30)  # 5-30 seconds
            
            # Assign priority with probabilities: 70% Normal, 20% Corporate, 10% VIP
            priority_roll = random.random()
            if priority_roll < 0.7:
                priority = Customer.PRIORITY_NORMAL
            elif priority_roll < 0.9:
                priority = Customer.PRIORITY_CORPORATE
            else:
                priority = Customer.PRIORITY_VIP
                
            customer = Customer(service_time, priority)
            self.scheduler.add_customer(customer)
    
    def _process_customer_completions(self):
        """Check for completed customers and remove them from agents"""
        while self.running:
            time.sleep(1)  # Check every second
            
            for agent in self.scheduler.agents:
                for customer in list(agent.assigned_customers):  # Create a copy to avoid modification issues
                    if customer.start_service_time and time.time() - customer.start_service_time >= customer.service_time:
                        self.scheduler.complete_customer(customer.id)
    
    def _run_simulation(self):
        """Main simulation loop"""
        while self.running:
            # Assign customers to available agents
            self.scheduler.assign_customers()
            
            # Sleep for a short interval before the next update
            time.sleep(0.5)
