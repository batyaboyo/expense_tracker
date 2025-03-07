// static/js/main.js
$(document).ready(function() {
    let simulationRunning = false;
    let updateInterval;

    // Event Handlers
    $('#startBtn').click(startSimulation);
    $('#stopBtn').click(stopSimulation);
    $('#algorithmSelect').change(updateAlgorithm);
    $('#applySettingsBtn').click(updateSettings);
    $('#addAgentBtn').click(function() {
        $('#addAgentModal').modal('show');
    });
    $('#confirmAddAgent').click(addNewAgent);
    
    // Update the arrival rate display
    $('#arrivalRateRange').on('input', function() {
        $('#arrivalRateValue').text($(this).val());
    });

    // Initial state update
    updateState();

    function startSimulation() {
        $.ajax({
            url: '/api/start',
            type: 'POST',
            success: function(response) {
                if (response.success) {
                    simulationRunning = true;
                    $('#startBtn').prop('disabled', true);
                    $('#stopBtn').prop('disabled', false);
                    
                    // Start the update interval
                    updateInterval = setInterval(updateState, 1000);
                }
            }
        });
    }

    function stopSimulation() {
        $.ajax({
            url: '/api/stop',
            type: 'POST',
            success: function(response) {
                if (response.success) {
                    simulationRunning = false;
                    $('#startBtn').prop('disabled', false);
                    $('#stopBtn').prop('disabled', true);
                    
                    // Clear the update interval
                    clearInterval(updateInterval);
                }
            }
        });
    }

    function updateAlgorithm() {
        const algorithm = $('#algorithmSelect').val();
        
        $.ajax({
            url: '/api/algorithm',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ algorithm: algorithm }),
            success: function(response) {
                if (response.success) {
                    // Flash the algorithm dropdown to indicate success
                    $('#algorithmSelect').addClass('border-success');
                    setTimeout(function() {
                        $('#algorithmSelect').removeClass('border-success');
                    }, 1000);
                }
            }
        });
    }

    function updateSettings() {
        const arrivalRate = $('#arrivalRateRange').val();
        const minServiceTime = $('#minServiceTime').val();
        const maxServiceTime = $('#maxServiceTime').val();
        
        $.ajax({
            url: '/api/settings',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                arrival_rate: arrivalRate,
                min_service_time: minServiceTime,
                max_service_time: maxServiceTime
            }),
            success: function(response) {
                if (response.success) {
                    // Flash the button to indicate success
                    $('#applySettingsBtn').removeClass('btn-info').addClass('btn-success');
                    setTimeout(function() {
                        $('#applySettingsBtn').removeClass('btn-success').addClass('btn-info');
                    }, 1000);
                }
            }
        });
    }

    function addNewAgent() {
        const name = $('#agentName').val();
        const maxWorkload = $('#maxWorkload').val();
        
        if (!name) {
            alert('Please enter an agent name');
            return;
        }
        
        $.ajax({
            url: '/api/agent',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: name,
                max_workload: maxWorkload
            }),
            success: function(response) {
                if (response.success) {
                    $('#addAgentModal').modal('hide');
                    $('#agentName').val('');
                    $('#maxWorkload').val(1);
                    updateState();
                }
            }
        });
    }

    function updateState() {
        $.ajax({
            url: '/api/state',
            type: 'GET',
            success: function(state) {
                updateMetrics(state.statistics);
                updateAgents(state.agents);
                updateCustomerQueue(state.queue);
            }
        });
    }

    function updateMetrics(statistics) {
        $('#avgWaitTime').text(formatTime(statistics.average_waiting_time));
        $('#utilization').text(Math.round(statistics.average_utilization) + '%');
        $('#fairness').text(Math.round(statistics.fairness) + '%');
        $('#completedCustomers').text(statistics.completed_customers);
        $('#waitingCustomers').text(statistics.waiting_customers);
    }

    function updateAgents(agents) {
        const agentsList = $('#agentsList');
        agentsList.empty();
        
        agents.forEach(function(agent) {
            const statusClass = agent.status === 'available' ? 'agent-available' : 'agent-busy';
            const statusBadge = agent.status === 'available' ? 
                '<span class="badge badge-success">Available</span>' : 
                '<span class="badge badge-danger">Busy</span>';
            
            const utilizationPercentage = Math.round(agent.utilization_rate);
            
            const agentCard = `
                <div class="agent-card ${statusClass}">
                    <h5>${agent.name}</h5>
                    ${statusBadge}
                    <p class="mb-1">Workload: ${agent.current_workload} / ${agent.max_workload}</p>
                    <p class="mb-1">Utilization: ${utilizationPercentage}%</p>
                    <div class="progress">
                        <div class="progress-bar bg-info" role="progressbar" style="width: ${utilizationPercentage}%" 
                            aria-valuenow="${utilizationPercentage}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
            `;
            
            agentsList.append(agentCard);
        });
    }

    function updateCustomerQueue(queue) {
        const customerQueue = $('#customerQueue');
        customerQueue.empty();
        
        queue.forEach(function(customer) {
            let statusClass = '';
            let badgeClass = '';
            let badgeText = '';
            
            // Set status class
            if (customer.status === 'Waiting') {
                statusClass = 'status-waiting';
            } else if (customer.status === 'In Service') {
                statusClass = 'status-in-service';
            } else {
                statusClass = 'status-completed';
            }
            
            // Set priority badge
            if (customer.priority === 2) {
                badgeClass = 'badge-vip';
                badgeText = 'VIP';
            } else if (customer.priority === 1) {
                badgeClass = 'badge-corporate';
                badgeText = 'Corporate';
            } else {
                badgeClass = 'badge-normal';
                badgeText = 'Normal';
            }
            
            const customerCard = `
                <div class="customer-card ${statusClass}">
                    <span class="badge ${badgeClass}">${badgeText}</span>
                    <h6>Customer ${customer.id.substring(0, 6)}</h6>
                    <p class="mb-1">Status: ${customer.status}</p>
                    <p class="mb-1">Service time: ${formatTime(customer.service_time)}</p>
                    <p class="mb-1">Waiting: ${formatTime(customer.waiting_time)}</p>
                    <div class="progress">
                        <div class="progress-bar bg-success" role="progressbar" style="width: ${customer.progress}%" 
                            aria-valuenow="${customer.progress}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
            `;
            
            customerQueue.append(customerCard);
        });
    }

    function formatTime(seconds) {
        seconds = Math.round(seconds);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        if (minutes > 0) {
            return `${minutes}m ${remainingSeconds}s`;
        } else {
            return `${remainingSeconds}s`;
        }
    }
});
