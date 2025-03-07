# models/customer.py
import time
import uuid

class Customer:
    PRIORITY_NORMAL = 0
    PRIORITY_CORPORATE = 1
    PRIORITY_VIP = 2

    PRIORITY_NAMES = {
        PRIORITY_NORMAL: "Normal",
        PRIORITY_CORPORATE: "Corporate",
        PRIORITY_VIP: "VIP"
    }

    def __init__(self, service_time, priority=PRIORITY_NORMAL):
        self.id = str(uuid.uuid4())
        self.service_time = service_time
        self.priority = priority
        self.arrival_time = time.time()
        self.start_service_time = None
        self.completion_time = None
        self.assigned_agent = None

    def assign_agent(self, agent):
        self.assigned_agent = agent
        self.start_service_time = time.time()
        
    def complete_service(self):
        self.completion_time = time.time()
        
    @property
    def waiting_time(self):
        if self.start_service_time:
            return self.start_service_time - self.arrival_time
        return time.time() - self.arrival_time
    
    @property
    def total_time(self):
        if self.completion_time:
            return self.completion_time - self.arrival_time
        return time.time() - self.arrival_time
    
    @property
    def service_progress(self):
        if not self.start_service_time:
            return 0
        if self.completion_time:
            return 100
        elapsed = time.time() - self.start_service_time
        progress = min(100, (elapsed / self.service_time) * 100)
        return progress
    
    @property
    def status(self):
        if self.completion_time:
            return "Completed"
        if self.start_service_time:
            return "In Service"
        return "Waiting"
    
    @property
    def priority_name(self):
        return self.PRIORITY_NAMES.get(self.priority, "Unknown")
    
    def to_dict(self):
        return {
            "id": self.id,
            "service_time": self.service_time,
            "priority": self.priority,
            "priority_name": self.priority_name,
            "arrival_time": self.arrival_time,
            "waiting_time": self.waiting_time,
            "total_time": self.total_time,
            "status": self.status,
            "progress": self.service_progress,
            "assigned_agent": self.assigned_agent.id if self.assigned_agent else None
        }
