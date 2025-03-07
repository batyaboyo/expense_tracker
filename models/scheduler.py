# models/scheduler.py
import random
import time
from .customer import Customer
from .agent import Agent

class Scheduler:
    ALGORITHM_ROUND_ROBIN = "round_robin"
    ALGORITHM_PRIORITY = "priority"
    ALGORITHM_SHORTEST_JOB_NEXT = "shortest_job_next"
    
    def __init__(self):
        self.queue = []
        self.agents = []
        self.completed_customers = []
        self.algorithm = self.ALGORITHM_ROUND_ROBIN
        self.last_agent_index = -1
        
    def add_agent(self, name, max_workload=1):
        agent = Agent(name, max_workload)
        self.agents.append(agent)
        return agent
        
    def add_customer(self, service_time=None, priority=None):
        if service_time is None:
            service_time = random.randint(20, 180)  # Random service time between 20s and 3m
        
        if priority is None:
            # Distribution: 70% Normal, 20% Corporate, 10% VIP
            rand = random.random()
            if rand < 0.7:
                priority = Customer.PRIORITY_NORMAL
            elif rand < 0.9:
                priority = Customer.PRIORITY_CORPORATE
            else:
                priority = Customer.PRIORITY_VIP
                
        customer = Customer(service_time, priority)
        self.queue.append(customer)
        return customer
    
    def assign_customers(self):
        """Assign customers to available agents based on the selected algorithm"""
        if not self.queue:
            return []  # No customers waiting
            
        # Sort the queue based on the selected algorithm
        if self.algorithm == self.ALGORITHM_PRIORITY:
            # Sort by priority (highest first) and then by arrival time
            self.queue.sort(key=lambda c: (-c.priority, c.arrival_time))
        elif self.algorithm == self.ALGORITHM_SHORTEST_JOB_NEXT:
            # Sort by service time (shortest first)
            self.queue.sort(key=lambda c: c.service_time)
        # Round Robin doesn't require sorting
        
        assigned = []
        available_agents = [a for a in self.agents if a.current_workload < a.max_workload]
        
        if not available_agents:
            return []  # No available agents
            
        if self.algorithm == self.ALGORITHM_ROUND_ROBIN:
            # Use modulo to cycle through available agents
            for customer in list(self.queue):
                # Find the next available agent in round-robin fashion
                agent_found = False
                for _ in range(len(available_agents)):
                    self.last_agent_index = (self.last_agent_index + 1) % len(available_agents)
                    agent = available_agents[self.last_agent_index]
                    if agent.current_workload < agent.max_workload:
                        agent_found = True
                        break
                
                if agent_found:
                    agent.assign_customer(customer)
                    customer.assign_agent(agent)
                    self.queue.remove(customer)
                    assigned.append(customer)
                    
                    # If agent reaches max workload, remove from available
                    if agent.current_workload >= agent.max_workload:
                        available_agents.remove(agent)
                        
                    if not available_agents:
                        break
        else:
            # For Priority and Shortest Job Next
            for customer in list(self.queue):
                for agent in available_agents:
                    if agent.current_workload < agent.max_workload:
                        agent.assign_customer(customer)
                        customer.assign_agent(agent)
                        self.queue.remove(customer)
                        assigned.append(customer)
                        
                        # If agent reaches max workload, remove from available
                        if agent.current_workload >= agent.max_workload:
                            available_agents.remove(agent)
                            
                        if not available_agents:
                            break
                
                if not available_agents:
                    break
                    
        return assigned
    
    def update_customer_progress(self):
        """Check for completed customers and update their status"""
        now = time.time()
        completed = []
        
        for agent in self.agents:
            for customer in list(agent.customers):
                if customer.start_service_time:
                    elapsed = now - customer.start_service_time
                    if elapsed >= customer.service_time:
                        customer.complete_service()
                        agent.complete_customer(customer.id)
                        self.completed_customers.append(customer)
                        completed.append(customer)
        
        return completed
    
    def get_statistics(self):
        """Calculate performance metrics"""
        total_waiting_time = 0
        total_customers = len(self.completed_customers)
        
        for customer in self.completed_customers:
            total_waiting_time += customer.waiting_time
        
        avg_waiting_time = total_waiting_time / total_customers if total_customers > 0 else 0
        
        # Calculate agent utilization
        utilization_rates = [agent.utilization_rate for agent in self.agents]
        avg_utilization = sum(utilization_rates) / len(utilization_rates) if self.agents else 0
        
        # Calculate fairness (standard deviation of workload distribution)
        workloads = [len(agent.customers) + agent.total_service_time for agent in self.agents]
        avg_workload = sum(workloads) / len(workloads) if self.agents else 0
        fairness = sum((w - avg_workload) ** 2 for w in workloads) / len(workloads) if self.agents else 0
        fairness = 100 - min(100, fairness * 10)  # Convert to a 0-100 scale where 100 is perfectly fair
        
        return {
            "average_waiting_time": avg_waiting_time,
            "average_utilization": avg_utilization,
            "fairness": fairness,
            "completed_customers": total_customers,
            "waiting_customers": len(self.queue)
        }
    
    def set_algorithm(self, algorithm):
        """Set the scheduling algorithm"""
        if algorithm in [self.ALGORITHM_ROUND_ROBIN, self.ALGORITHM_PRIORITY, self.ALGORITHM_SHORTEST_JOB_NEXT]:
            self.algorithm = algorithm
            return True
        return False
    
    def get_state(self):
        """Get the current state of the system"""
        return {
            "queue": [c.to_dict() for c in self.queue],
            "agents": [a.to_dict() for a in self.agents],
            "completed": len(self.completed_customers),
            "algorithm": self.algorithm,
            "statistics": self.get_statistics()
        }
