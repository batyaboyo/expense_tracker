# models/agent.py
import time
import uuid

class Agent:
    STATUS_AVAILABLE = "available"
    STATUS_BUSY = "busy"

    def __init__(self, name, max_workload=1):
        self.id = str(uuid.uuid4())
        self.name = name
        self.max_workload = max_workload
        self.current_workload = 0
        self.status = self.STATUS_AVAILABLE
        self.customers = []
        self.total_service_time = 0
        self.busy_since = None
        self.creation_time = time.time()
        
    def assign_customer(self, customer):
        if self.current_workload < self.max_workload:
            self.customers.append(customer)
            self.current_workload += 1
            if self.current_workload == 1:  # First customer
                self.busy_since = time.time()
            if self.current_workload >= self.max_workload:
                self.status = self.STATUS_BUSY
            return True
        return False
        
    def complete_customer(self, customer_id):
        for i, customer in enumerate(self.customers):
            if customer.id == customer_id:
                self.total_service_time += customer.service_time
                self.customers.pop(i)
                self.current_workload -= 1
                if self.current_workload == 0:
                    self.status = self.STATUS_AVAILABLE
                    self.busy_since = None
                return True
        return False
    
    @property
    def utilization_rate(self):
        # Calculate utilization as the percentage of time spent serving customers
        if self.total_service_time == 0:
            return 0
        return min(100, (self.total_service_time / (time.time() - self.creation_time)) * 100)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "current_workload": self.current_workload,
            "max_workload": self.max_workload,
            "customers": [c.id for c in self.customers],
            "utilization_rate": self.utilization_rate
        }
