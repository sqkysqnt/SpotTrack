const devicesList = document.getElementById('devices-list');
const ssidSelect = document.getElementById('target_ssid');
const logsDiv = document.getElementById('logs-content');
const mqttInfoDiv = document.getElementById('mqtt-info-content');
const setupModal = document.getElementById('setupModal');
const deviceCheckboxes = document.getElementById('deviceCheckboxes');
const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = function(event) {
    const devices = JSON.parse(event.data);
    devicesList.innerHTML = '';
    deviceCheckboxes.innerHTML = '';
    for (const [device_id, device_info] of Object.entries(devices)) {
        const li = document.createElement('li');
        li.textContent = `ID: ${device_id}, Info: ${JSON.stringify(device_info)}`;
        devicesList.appendChild(li);

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = device_id;
        checkbox.name = device_id;
        checkbox.value = device_id;

        const label = document.createElement('label');
        label.htmlFor = device_id;
        label.appendChild(document.createTextNode(` ${device_id}`));

        deviceCheckboxes.appendChild(checkbox);
        deviceCheckboxes.appendChild(label);
        deviceCheckboxes.appendChild(document.createElement('br'));
    }
};

document.getElementById('configForm').onsubmit = function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const configData = {
        device_id: formData.get('device_id'),
        target_ssid: formData.get('target_ssid'),
        target_password: formData.get('target_password'),
        mode: formData.get('mode'),
        calibration_data: formData.get('calibration_data')
    };
    fetch('/send_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(configData),
    }).then(response => response.json())
      .then(data => addLog(`Configuration sent: ${JSON.stringify(configData)}`));
};


function searchSSIDs() {
    fetch('/search_ssids')
        .then(response => response.json())
        .then(data => {
            ssidSelect.innerHTML = '';
            data.ssids.forEach(ssid => {
                const option = document.createElement('option');
                option.value = ssid;
                option.textContent = ssid;
                ssidSelect.appendChild(option);
            });
            addLog('SSIDs searched');
        });
}

function openSetupModal() {
    setupModal.style.display = 'block';
}

function closeSetupModal() {
    setupModal.style.display = 'none';
}

function triggerSetupMode() {
    const checkboxes = document.querySelectorAll('#deviceCheckboxes input[type="checkbox"]');
    const selectedDevices = [];
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedDevices.push(checkbox.value);
        }
    });
    fetch('/setup_mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ devices: selectedDevices }),
    }).then(response => response.json())
      .then(data => {
          addLog(data.status);
          closeSetupModal();
      });
}

function addLog(message) {
    const p = document.createElement('p');
    p.textContent = message;
    logsDiv.appendChild(p);
}

function showTab(tabId) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');
}

function fetchMqttInfo() {
    fetch('/mqtt_info')
        .then(response => response.json())
        .then(data => {
            mqttInfoDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        });
}

document.addEventListener('DOMContentLoaded', function() {
    showTab('devices');
    fetchMqttInfo();
});
