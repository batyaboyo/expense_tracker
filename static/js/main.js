document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const algorithmSelect = document.getElementById('algorithm');
    const agentsContainer = document.getElementById('agents-container');
    const queueContainer = document.getElementById('queue-container');
    const activeCustomersContainer = document.getElementById('active-customers-container');
    const completedContainer = document.getElementById('completed-container');
    
    // Agent management elements
    const addAgentBtn = document.getElementById('add-agent-btn');
    const agentFormContainer = document.getElementById('agent-form-container');
    const addAgentForm = document.getElementById('add-agent-form');
    const cancelAddAgentBtn = document.getElementById('cancel-add-agent');
    
    // Metrics elements
    const avgWaitTimeEl = document.getElementById('avg-wait-time');
    const avgUtilizationEl = document.getElementById('avg-utilization');
    const fairnessEl = document.getElementById('fairness');
    const customersServedEl = document.getElementById('customers-served');
    
    // State management
    let isRunning = false;
    let updateInterval = null;
    let lastQueueIds = [];
    let lastActiveIds = [];
    let lastCompletedIds = [];
    
    // Event Listeners
    startBtn.addEventListener('click', startSimulation);
    stopBtn.addEventListener('click', stopSimulation);
    algorithmSelect.addEventListener('change', changeAlgorithm);
    
    // Agent management event listeners
    addAgentBtn.addEventListener('click', showAddAgentForm);
    cancelAddAgentBtn.addEventListener('click', hideAddAgentForm);
    addAgentForm.addEventListener('submit', handleAddAgent);
    
    // Functions
    function startSimulation() {
        fetch('/api/start', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'started') {
                isRunning = true;
                startBtn.disabled = true;
                stopBtn.disabled = false;
                // Start the update interval
                updateInterval = setInterval(updateState, 1000);
            }
        });
    }
    
    function stopSimulation() {
        fetch('/api/stop', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'stopped') {
                isRunning = false;
                startBtn.disabled = false;
                stopBtn.disabled = true;
                // Stop the update interval
                clearInterval(updateInterval);
            }
        });
    }
    
    function changeAlgorithm() {
        const algorithm = algorithmSelect.value;
        fetch('/api/algorithm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ algorithm })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Algorithm changed to:', data.algorithm);
        });
    }
    
    // Agent management functions
    function showAddAgentForm() {
        agentFormContainer.style.display = 'block';
        addAgentBtn.style.display = 'none';
    }
    
    function hideAddAgentForm() {
        agentFormContainer.style.display = 'none';
        addAgentBtn.style.display = 'block';
        // Reset form
        addAgentForm.reset();
    }
    
    function handleAddAgent(e) {
        e.preventDefault();
        
        const nameInput = document.getElementById('agent-name');
        const workloadSelect = document.getElementById('agent-workload');
        
        const name = nameInput.value;
        const max_workload = parseInt(workloadSelect.value);
        
        fetch('/api/agents/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, max_workload })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'agent added') {
                // Hide form and reset
                hideAddAgentForm();
                
                // Could update immediately or just wait for next update
                updateState();
            }
        });
    }
    
    function handleRemoveAgent(agentId) {
        // Visual feedback - mark agent as being removed
        const agentCard = document.querySelector(`[data-agent-id="${agentId}"]`);
        if (agentCard) {
            agentCard.classList.add('removing');
        }
        
        fetch('/api/agents/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ agent_id: agentId })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                // Update the UI
                updateState();
            }
        });
    }
    
    function updateState() {
        fetch('/api/state')
        .then(response => response.json())
        .then(data => {
            updateAgents(data.agents);
            updateQueue(data.queue);
            updateActiveCustomers(data.active_customers);
            updateCompletedCustomers(data.completed_customers);
            updateMetrics(data.metrics);
            
            // Also update the algorithm selector to match the server state
            if (algorithmSelect.value !== data.algorithm) {
                algorithmSelect.value = data.algorithm;
            }
        });
    }
    
    function updateAgents(agents) {
        agentsContainer.innerHTML = '';
        
        agents.forEach(agent => {
            const agentCard = document.createElement('div');
            agentCard.className = 'agent-card';
            agentCard.setAttribute('data-agent-id', agent.id);
            
            const workloadPercentage = (agent.current_workload / agent.max_workload) * 100;
            
            agentCard.innerHTML = `
                <div class="agent-status status-${agent.status}"></div>
                <div class="agent-name">${agent.name}</div>
                <div>Current Tasks: ${agent.current_workload}/${agent.max_workload}</div>
                <div class="agent-workload">
                    <div class="workload-fill" style="width: ${workloadPercentage}%"></div>
                </div>
                <button class="remove-agent-btn" data-agent-id="${agent.id}">Remove</button>
            `;
            
            agentsContainer.appendChild(agentCard);
            
            // Add event listener to the remove button
            const removeBtn = agentCard.querySelector('.remove-agent-btn');
            removeBtn.addEventListener('click', function() {
                handleRemoveAgent(agent.id);
            });
        });
    }
    
    function updateQueue(queue) {
        queueContainer.innerHTML = '';
        
        // Track which customers are new
        const currentQueueIds = queue.map(c => c.id);
        
        queue.forEach(customer => {
            const customerCard = createCustomerCard(customer);
            
            // Add animation for new customers
            if (!lastQueueIds.includes(customer.id)) {
                customerCard.classList.add('new-customer');
            }
            
            queueContainer.appendChild(customerCard);
        });
        
        lastQueueIds = currentQueueIds;
    }
    
    function updateActiveCustomers(activeCustomers) {
        activeCustomersContainer.innerHTML = '';
        
        // Track which customers are new
        const currentActiveIds = activeCustomers.map(c => c.id);
        
        activeCustomers.forEach(customer => {
            const customerCard = createCustomerCard(customer, true);
            
            // Add animation for new customers
            if (!lastActiveIds.includes(customer.id)) {
                customerCard.classList.add('new-customer');
            }
            
            activeCustomersContainer.appendChild(customerCard);
        });
        
        lastActiveIds = currentActiveIds;
    }
    
    function updateCompletedCustomers(completedCustomers) {
        completedContainer.innerHTML = '';
        
        // Show only the 10 most recent completed customers
        const recentCompleted = completedCustomers.slice(-10);
        
        // Track which customers are new
        const currentCompletedIds = recentCompleted.map(c => c.id);
        
        recentCompleted.forEach(customer => {
            const customerCard = createCustomerCard(customer);
            
            // Add animation for new customers
            if (!lastCompletedIds.includes(customer.id)) {
                customerCard.classList.add('new-customer');
            }
            
            completedContainer.appendChild(customerCard);
        });
        
        lastCompletedIds = currentCompletedIds;
    }
    
    function createCustomerCard(customer, isActive = false) {
        const customerCard = document.createElement('div');
        customerCard.className = 'customer-card';
        
        let timerLabel = 'Wait Time';
        let timerValue = `${customer.wait_time}s`;
        
        if (isActive) {
            // For active customers, show remaining service time
            const elapsedServiceTime = (Date.now() / 1000) - (customer.start_service_time || 0);
            const remainingTime = Math.max(0, customer.service_time - elapsedServiceTime).toFixed(1);
            timerLabel = 'Remaining';
            timerValue = `${remainingTime}s`;
        } else if (customer.completion_time) {
            // For completed customers, show total time
            const totalTime = ((customer.completion_time - customer.arrival_time) || 0).toFixed(1);
            timerLabel = 'Total Time';
            timerValue = `${totalTime}s`;
        }
        
        customerCard.innerHTML = `
            <div class="customer-priority priority-${customer.priority_name}"></div>
            <div class="customer-details">
                <div class="customer-id">Customer #${customer.id}</div>
                <div class="customer-info">
                    <span class="priority-badge priority-${customer.priority_name}-badge">${customer.priority_name}</span>
                    <span>Service: ${customer.service_time}s</span>
                </div>
            </div>
            <div class="customer-timer">
                <div class="timer-label">${timerLabel}</div>
                <div class="timer-value">${timerValue}</div>
            </div>
        `;
        
        return customerCard;
    }
    
    function updateMetrics(metrics) {
        avgWaitTimeEl.textContent = `${metrics.average_wait_time}s`;
        avgUtilizationEl.textContent = `${(metrics.average_utilization * 100).toFixed(0)}%`;
        fairnessEl.textContent = `${(metrics.fairness * 100).toFixed(0)}%`;
        customersServedEl.textContent = metrics.completed_customers;
    }
    
    // Initial update
    updateState();
});
