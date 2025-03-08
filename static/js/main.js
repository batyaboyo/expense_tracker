// System state
let agents = [];
let customers = [];
let waitQueue = [];
let simulationRunning = false;
let simulationInterval;
let customerArrivalInterval;
let systemUpdateInterval;
let currentTime = 0;
let customerIdCounter = 1;
let customersServed = 0;
let totalWaitTime = 0;
let maxWaitTime = 0;
let agentUtilizationData = [];

// Customer types and service times
const customerTypes = ['normal', 'corporate', 'vip'];
const customerPriorities = {
    'normal': 1,
    'corporate': 2,
    'vip': 3
};

// Initialize agents
function initializeAgents(count) {
    agents = [];
    for (let i = 0; i < count; i++) {
        agents.push({
            id: i + 1,
            name: `Agent ${i + 1}`,
            available: true,
            workload: 0,
            maxWorkload: 5,
            tasksCompleted: 0,
            totalWorkTime: 0,
            customer: null
        });
    }
    renderAgents();
}

// Generate a random customer
function generateCustomer() {
    const type = customerTypes[Math.floor(Math.random() * customerTypes.length)];
    // Service time between 30 seconds and 5 minutes
    const serviceTime = Math.floor(Math.random() * (300 - 30 + 1)) + 30;
    return {
        id: customerIdCounter++,
        type: type,
        priority: customerPriorities[type],
        serviceTime: serviceTime,
        remainingTime: serviceTime,
        arrivalTime: currentTime,
        waitTime: 0,
        inService: false,
        assignedAgent: null
    };
}

// Add a customer to the queue
function addCustomerToQueue() {
    const customer = generateCustomer();
    waitQueue.push(customer);
    renderCustomers();
    renderQueueVisualization();
    updateMetrics();
}

// Round Robin scheduling algorithm
function roundRobinScheduling() {
    if (waitQueue.length === 0) return;
    
    // Find the next available agent
    const availableAgents = agents.filter(agent => agent.available);
    if (availableAgents.length === 0) return;
    
    // Take the first customer in the queue
    const customer = waitQueue.shift();
    const agent = availableAgents[0];
    
    assignCustomerToAgent(customer, agent);
}

// Priority-based scheduling algorithm
function priorityScheduling() {
    if (waitQueue.length === 0) return;
    
    // Find the next available agent
    const availableAgents = agents.filter(agent => agent.available);
    if (availableAgents.length === 0) return;
    
    // Sort the queue by priority (highest first)
    waitQueue.sort((a, b) => b.priority - a.priority);
    
    // Take the highest priority customer
    const customer = waitQueue.shift();
    const agent = availableAgents[0];
    
    assignCustomerToAgent(customer, agent);
}

// Shortest Job Next scheduling algorithm
function shortestJobNextScheduling() {
    if (waitQueue.length === 0) return;
    
    // Find the next available agent
    const availableAgents = agents.filter(agent => agent.available);
    if (availableAgents.length === 0) return;
    
    // Sort the queue by service time (shortest first)
    waitQueue.sort((a, b) => a.serviceTime - b.serviceTime);
    
    // Take the customer with the shortest service time
    const customer = waitQueue.shift();
    const agent = availableAgents[0];
    
    assignCustomerToAgent(customer, agent);
}

// Assign a customer to an agent
function assignCustomerToAgent(customer, agent) {
    customer.inService = true;
    customer.assignedAgent = agent.id;
    customer.waitTime = currentTime - customer.arrivalTime;
    
    // Update metrics
    totalWaitTime += customer.waitTime;
    maxWaitTime = Math.max(maxWaitTime, customer.waitTime);
    
    // Update agent
    agent.available = false;
    agent.workload++;
    agent.customer = customer;
    
    customers.push(customer);
    
    renderAgents();
    renderCustomers();
    renderQueueVisualization();
    updateMetrics();
}

// Update customer and agent status
function updateSystem() {
    currentTime += 5; // 5 second increments
    
    // Update clock
    document.getElementById('clock').textContent = formatTime(currentTime);
    
    // Process customer service
    for (let i = 0; i < agents.length; i++) {
        const agent = agents[i];
        if (!agent.available && agent.customer) {
            agent.customer.remainingTime -= 5;
            agent.totalWorkTime += 5;
            
            if (agent.customer.remainingTime <= 0) {
                // Service completed
                agent.available = true;
                agent.tasksCompleted++;
                
                // Remove customer from the active list
                const index = customers.findIndex(c => c.id === agent.customer.id);
                if (index !== -1) {
                    customers.splice(index, 1);
                }
                
                customersServed++;
                agent.customer = null;
            }
        }
    }
    
    // Update wait times for queued customers
    for (let i = 0; i < waitQueue.length; i++) {
        waitQueue[i].waitTime = currentTime - waitQueue[i].arrivalTime;
    }
    
    // Collect agent utilization data
    agentUtilizationData.push(
        agents.filter(agent => !agent.available).length / agents.length
    );
    if (agentUtilizationData.length > 30) {
        agentUtilizationData.shift(); // Keep last 30 data points
    }
    
    // Apply scheduling algorithm
    const algorithm = document.getElementById('algorithm').value;
    if (algorithm === 'round-robin') {
        roundRobinScheduling();
    } else if (algorithm === 'priority') {
        priorityScheduling();
    } else if (algorithm === 'sjn') {
        shortestJobNextScheduling();
    }
    
    renderAgents();
    renderCustomers();
    renderQueueVisualization();
    updateMetrics();
}

// Render agent cards
function renderAgents() {
    const agentGrid = document.getElementById('agent-grid');
    agentGrid.innerHTML = '';
    
    agents.forEach(agent => {
        const card = document.createElement('div');
        card.className = `agent-card ${agent.available ? '' : 'busy'}`;
        
        const statusClass = agent.available ? 'status-available' : 'status-busy';
        const workloadPercentage = (agent.workload / agent.maxWorkload) * 100;
        
        card.innerHTML = `
            <h4>${agent.name}</h4>
            <p>
                <span class="status-indicator ${statusClass}"></span>
                ${agent.available ? 'Available' : 'Busy'}
            </p>
            <p>Tasks: ${agent.tasksCompleted}</p>
            <p>Workload: ${agent.workload}/${agent.maxWorkload}</p>
            <div class="progress-bar">
                <div class="progress" style="width: ${workloadPercentage}%"></div>
            </div>
            ${agent.customer ? `<p>Serving: Customer #${agent.customer.id} (${formatTime(agent.customer.remainingTime)} left)</p>` : ''}
        `;
        
        agentGrid.appendChild(card);
    });
    
    // Update active agents count
    document.getElementById('active-agents').textContent = agents.filter(a => !a.available).length;
}

// Render customer cards
function renderCustomers() {
    const customerGrid = document.getElementById('customer-grid');
    customerGrid.innerHTML = '';
    
    // First show customers being served
    customers.forEach(customer => {
        const card = document.createElement('div');
        card.className = `customer-card ${customer.type}`;
        
        card.innerHTML = `
            <h4>Customer #${customer.id}</h4>
            <p>Type: ${customer.type.charAt(0).toUpperCase() + customer.type.slice(1)}</p>
            <p>Wait Time: ${formatTime(customer.waitTime)}</p>
            <p>Service Time: ${formatTime(customer.serviceTime)}</p>
            <p>Remaining: ${formatTime(customer.remainingTime)}</p>
            ${customer.assignedAgent ? `<p>Agent: #${customer.assignedAgent}</p>` : ''}
        `;
        
        customerGrid.appendChild(card);
    });
    
    // Then show waiting customers
    waitQueue.forEach(customer => {
        const card = document.createElement('div');
        card.className = `customer-card ${customer.type}`;
        
        card.innerHTML = `
            <h4>Customer #${customer.id} (Waiting)</h4>
            <p>Type: ${customer.type.charAt(0).toUpperCase() + customer.type.slice(1)}</p>
            <p>Wait Time: ${formatTime(customer.waitTime)}</p>
            <p>Service Time: ${formatTime(customer.serviceTime)}</p>
        `;
        
        customerGrid.appendChild(card);
    });
    
    // Update waiting customers count
    document.getElementById('waiting-customers').textContent = waitQueue.length;
}

// Render queue visualization
function renderQueueVisualization() {
    const queueViz = document.getElementById('queue-visualization');
    queueViz.innerHTML = '';
    
    waitQueue.forEach(customer => {
        const queueItem = document.createElement('div');
        queueItem.className = `queue-item ${customer.type}`;
        queueItem.textContent = customer.id;
        queueItem.title = `Customer #${customer.id} - ${customer.type}, Wait: ${formatTime(customer.waitTime)}`;
        
        queueViz.appendChild(queueItem);
    });
    
    if (waitQueue.length === 0) {
        queueViz.innerHTML = '<p>No customers in queue</p>';
    }
}

// Update performance metrics
function updateMetrics() {
    // Calculate average wait time
    const avgWaitTime = customersServed > 0 ? totalWaitTime / customersServed : 0;
    document.getElementById('avg-wait-time').textContent = formatTime(avgWaitTime);
    
    // Update max wait time
    document.getElementById('max-wait-time').textContent = formatTime(maxWaitTime);
    
    // Calculate agent utilization (average of last 30 data points)
    let avgUtilization = 0;
    if (agentUtilizationData.length > 0) {
        avgUtilization = agentUtilizationData.reduce((sum, val) => sum + val, 0) / agentUtilizationData.length;
    }
    document.getElementById('agent-utilization').textContent = `${Math.round(avgUtilization * 100)}%`;
    
    // Update queue length
    document.getElementById('queue-length').textContent = waitQueue.length;
    
    // Update customers served
    document.getElementById('customers-served').textContent = customersServed;
    
    // Calculate system load
    const systemLoad = Math.min(1, (waitQueue.length / (agents.length * 3)));
    document.getElementById('system-load-progress').style.width = `${systemLoad * 100}%`;
    
    // Calculate fairness index (Jain's fairness index)
    let fairness = 1.0;
    if (agents.length > 1) {
        const taskCounts = agents.map(a => a.tasksCompleted);
        const sumSquared = Math.pow(taskCounts.reduce((a, b) => a + b, 0), 2);
        const sumOfSquares = taskCounts.reduce((a, b) => a + b * b, 0) * agents.length;
        fairness = sumSquared > 0 ? sumSquared / sumOfSquares : 1.0;
    }
    document.getElementById('fairness-index').textContent = fairness.toFixed(2);
}

// Format time in seconds to mm:ss format
function formatTime(seconds) {
    seconds = Math.floor(seconds);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Start simulation
function startSimulation() {
    if (simulationRunning) return;
    
    simulationRunning = true;
    document.getElementById('start-btn').disabled = true;
    document.getElementById('pause-btn').disabled = false;
    
    // Start system update interval (every 5 seconds)
    systemUpdateInterval = setInterval(updateSystem, 1000);
    
    // Start customer arrival
    const arrivalRate = parseInt(document.getElementById('arrival-rate').value);
    customerArrivalInterval = setInterval(addCustomerToQueue, arrivalRate * 1000);
}

// Pause simulation
function pauseSimulation() {
    simulationRunning = false;
    document.getElementById('start-btn').disabled = false;
    document.getElementById('pause-btn').disabled = true;
    
    clearInterval(systemUpdateInterval);
    clearInterval(customerArrivalInterval);
}

// Reset simulation
function resetSimulation() {
    pauseSimulation();
    
    // Reset all data
    waitQueue = [];
    customers = [];
    customersServed = 0;
    totalWaitTime = 0;
    maxWaitTime = 0;
    currentTime = 0;
    customerIdCounter = 1;
    agentUtilizationData = [];
    
    const agentCount = parseInt(document.getElementById('agent-count').value);
    initializeAgents(agentCount);
    
    renderCustomers();
    renderQueueVisualization();
    updateMetrics();
    
    document.getElementById('clock').textContent = formatTime(currentTime);
}

// Initialize the app
function initApp() {
    // Initialize agents
    const initialAgentCount = parseInt(document.getElementById('agent-count').value);
    initializeAgents(initialAgentCount);
    
    // Set up event listeners
    document.getElementById('start-btn').addEventListener('click', startSimulation);
    document.getElementById('pause-btn').addEventListener('click', pauseSimulation);
    document.getElementById('reset-btn').addEventListener('click', resetSimulation);
    document.getElementById('update-agents-btn').addEventListener('click', function() {
        const agentCount = parseInt(document.getElementById('agent-count').value);
        initializeAgents(agentCount);
    });
    
    // Set up tab switching
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and contents
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and its content
            this.classList.add('active');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Initialize metrics
    updateMetrics();
    
    // Initialize clock
    document.getElementById('clock').textContent = formatTime(currentTime);
    
    // Disable pause button initially
    document.getElementById('pause-btn').disabled = true;
}

// Start the app when page loads
window.addEventListener('load', initApp);
