document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const resetBtn = document.getElementById('resetBtn');
    const trainingToggle = document.getElementById('trainingToggle');

// Stats elements
const episodeValue = document.getElementById('episodeValue');
const stepValue = document.getElementById('stepValue');
const waitingTimeValue = document.getElementById('waitingTimeValue');
const rewardValue = document.getElementById('rewardValue');
const epsilonValue = document.getElementById('epsilonValue');
const carsPassedValue = document.getElementById('carsPassedValue');

// Traffic light elements
const lightNorth = document.getElementById('lightNorth');
const lightSouth = document.getElementById('lightSouth');
const lightEast = document.getElementById('lightEast');
const lightWest = document.getElementById('lightWest');

// Queue elements
const queueNorth = document.getElementById('queueNorth');
const queueSouth = document.getElementById('queueSouth');
const queueEast = document.getElementById('queueEast');
const queueWest = document.getElementById('queueWest');

// History panels
const actionHistory = document.getElementById('actionHistory');
const episodeSummary = document.getElementById('episodeSummary');

// Simulation state
let isSimulationRunning = false;
let isTrainingMode = false;

// Event listeners
startBtn.addEventListener('click', startSimulation);
stopBtn.addEventListener('click', stopSimulation);
resetBtn.addEventListener('click', resetSimulation);
trainingToggle.addEventListener('change', toggleTraining);

// Socket.IO event handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    stopSimulation();
});

socket.on('update_ui', (data) => {
    updateStats(data);
    updateTrafficLights(data.lights);
    updateQueues(data.queues);
    updateActionHistory(data.step, data.action, data.reward);
});

socket.on('episode_summary', (data) => {
    addEpisodeSummary(data);
});

socket.on('simulation_reset', () => {
    resetUI();
});

socket.on('training_status', (data) => {
    isTrainingMode = data.training;
    trainingToggle.checked = isTrainingMode;
});

// Functions
function startSimulation() {
    isSimulationRunning = true;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    resetBtn.disabled = true;
    trainingToggle.disabled = true;
    
    socket.emit('start_simulation', { training: isTrainingMode });
}

function stopSimulation() {
    isSimulationRunning = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    resetBtn.disabled = false;
    trainingToggle.disabled = false;
    
    socket.emit('stop_simulation');
}

function resetSimulation() {
    resetUI();
    socket.emit('reset_simulation');
}

function toggleTraining() {
    isTrainingMode = trainingToggle.checked;
    socket.emit('toggle_training', { training: isTrainingMode });
}

function resetUI() {
    // Reset stats
    episodeValue.textContent = '0';
    stepValue.textContent = '0';
    waitingTimeValue.textContent = '0';
    rewardValue.textContent = '0';
    carsPassedValue.textContent = '0';
    
    // Reset traffic lights
    updateTrafficLights({
        'North': 0,
        'South': 0,
        'East': 0,
        'West': 0
    });
    
    // Reset queues
    updateQueues({
        'North': 0,
        'South': 0,
        'East': 0,
        'West': 0
    });
    
    // Clear history
    actionHistory.innerHTML = '';
    episodeSummary.innerHTML = '';
}

function updateStats(data) {
    episodeValue.textContent = data.episode;
    stepValue.textContent = data.step;
    waitingTimeValue.textContent = data.waiting_time;
    rewardValue.textContent = data.reward;
    epsilonValue.textContent = data.epsilon;
    carsPassedValue.textContent = data.cars_passed;
}

function updateTrafficLights(lights) {
    // Update North traffic light
    const northRed = lightNorth.querySelector('.red');
    const northGreen = lightNorth.querySelector('.green');
    if (lights['North'] === 1) {
        northRed.classList.remove('active');
        northGreen.classList.add('active');
    } else {
        northRed.classList.add('active');
        northGreen.classList.remove('active');
    }
    
    // Update South traffic light
    const southRed = lightSouth.querySelector('.red');
    const southGreen = lightSouth.querySelector('.green');
    if (lights['South'] === 1) {
        southRed.classList.remove('active');
        southGreen.classList.add('active');
    } else {
        southRed.classList.add('active');
        southGreen.classList.remove('active');
    }
    
    // Update East traffic light
    const eastRed = lightEast.querySelector('.red');
    const eastGreen = lightEast.querySelector('.green');
    if (lights['East'] === 1) {
        eastRed.classList.remove('active');
        eastGreen.classList.add('active');
    } else {
        eastRed.classList.add('active');
        eastGreen.classList.remove('active');
    }
    
    // Update West traffic light
    const westRed = lightWest.querySelector('.red');
    const westGreen = lightWest.querySelector('.green');
    if (lights['West'] === 1) {
        westRed.classList.remove('active');
        westGreen.classList.add('active');
    } else {
        westRed.classList.add('active');
        westGreen.classList.remove('active');
    }
}

function updateQueues(queues) {
    // Clear current queues
    queueNorth.innerHTML = '';
    queueSouth.innerHTML = '';
    queueEast.innerHTML = '';
    queueWest.innerHTML = '';
    
    // Add cars to queues
    for (let i = 0; i < queues['North']; i++) {
        const car = document.createElement('div');
        car.className = 'car';
        queueNorth.appendChild(car);
    }
    
    for (let i = 0; i < queues['South']; i++) {
        const car = document.createElement('div');
        car.className = 'car';
        queueSouth.appendChild(car);
    }
    
    for (let i = 0; i < queues['East']; i++) {
        const car = document.createElement('div');
        car.className = 'car';
        queueEast.appendChild(car);
    }
    
    for (let i = 0; i < queues['West']; i++) {
        const car = document.createElement('div');
        car.className = 'car';
        queueWest.appendChild(car);
    }
}

function updateActionHistory(step, action, reward) {
    const actionItem = document.createElement('div');
    actionItem.className = 'action-item';
    actionItem.innerHTML = `
        <span>Step ${step}: ${action}</span>
        <span>Reward: ${reward}</span>
    `;
    
    // Add to the top of the history
    if (actionHistory.firstChild) {
        actionHistory.insertBefore(actionItem, actionHistory.firstChild);
    } else {
        actionHistory.appendChild(actionItem);
    }
    
    // Limit history items
    if (actionHistory.children.length > 50) {
        actionHistory.removeChild(actionHistory.lastChild);
    }
}

function addEpisodeSummary(data) {
    const summary = document.createElement('div');
    summary.className = 'episode-summary';
    summary.innerHTML = `
        <strong>Episode ${data.episode}</strong><br>
        Average Reward: ${data.avg_reward}<br>
        Total Waiting Time: ${data.total_waiting_time}<br>
        Cars Passed: ${data.cars_passed}<br>
        Actions: ${data.action_history.filter((a, i) => i % 5 === 0).join(', ')}...
    `;
    
    // Add to the top of the summary list
    if (episodeSummary.firstChild) {
        episodeSummary.insertBefore(summary, episodeSummary.firstChild);
    } else {
        episodeSummary.appendChild(summary);
    }
    
    // Limit summary items
    if (episodeSummary.children.length > 20) {
        episodeSummary.removeChild(episodeSummary.lastChild);
    }
}

// Initialize UI on page load
resetUI();
});