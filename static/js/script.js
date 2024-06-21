const devicesList = document.getElementById('devices-list');
const ssidSelect = document.getElementById('target_ssid');
const logsDiv = document.getElementById('logs-content');
const mqttInfoDiv = document.getElementById('mqtt-info-content');
const setupModal = document.getElementById('setupModal');
const modeWarningModal = document.getElementById('modeWarningModal');
const modeWarningText = document.getElementById('modeWarningText');
const deviceCheckboxes = document.getElementById('deviceCheckboxes');
const modeDisplay = document.getElementById('mode-display');
const header = document.getElementById('main-header');
let currentMode = 'Unknown';
const anchors = {};

const ws = new WebSocket(`ws://${window.location.host}/ws`);

ws.onmessage = function(event) {
    console.log('Received WebSocket message:', event.data);
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

document.getElementById('wifiForm').onsubmit = function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const configData = {
        device_id: formData.get('device_id'),
        ssid: formData.get('target_ssid'),
        password: formData.get('target_password')
    };
    fetch('/send_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(configData),
    }).then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => addLog(`WiFi configuration sent: ${JSON.stringify(configData)}`))
    .catch(error => addLog(`Failed to send configuration: ${error}`));
};

document.getElementById('anchorForm').onsubmit = function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const anchorUpdate = {
        mac_address: formData.get('anchor_mac').split(' - ')[0], // Extract only the MAC address
        user_defined_name: formData.get('anchor_name'),
        user_defined_location: formData.get('anchor_location')
    };
    fetch('/update_anchor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(anchorUpdate),
    }).then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => addLog(`Anchor updated: ${JSON.stringify(anchorUpdate)}`))
    .catch(error => addLog(`Failed to update anchor: ${error}`));
};

document.getElementById('modeForm').onsubmit = function(event) {
    event.preventDefault();
    const newMode = document.getElementById('mode').value;
    showModeWarning(currentMode, newMode);
};

function searchSSIDs() {
    const searchButton = document.getElementById('search-ssids-button');
    searchButton.disabled = true;
    searchButton.textContent = 'Searching...';

    fetch('/search_ssids')
        .then(response => response.json())
        .then(data => {
            const ssidSelect = document.getElementById('target_ssid');
            ssidSelect.innerHTML = '';
            data.ssids.forEach(ssid => {
                const option = document.createElement('option');
                option.value = ssid;
                option.textContent = ssid;
                ssidSelect.appendChild(option);
            });
            searchButton.disabled = false;
            searchButton.textContent = 'Search SSIDs';
            addLog('SSIDs searched successfully');
        }).catch(error => {
            searchButton.disabled = false;
            searchButton.textContent = 'Search SSIDs';
            addLog(`Failed to search SSIDs: ${error}`);
        });
}

document.getElementById('search-ssids-button').addEventListener('click', searchSSIDs);

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
            mqttInfoDiv.innerHTML = `
                <pre>Broker Information: ${JSON.stringify(data.broker_info, null, 2)}</pre>
                <pre>Client Information: ${JSON.stringify(data.client_info, null, 2)}</pre>
            `;
        }).catch(error => {
            addLog(`Failed to fetch MQTT info: ${error}`);
        });
}

function showModeWarning(fromMode, toMode) {
    modeWarningText.textContent = `You are about to change the mode from ${fromMode} to ${toMode}. Are you sure?`;
    modeWarningModal.style.display = 'block';
}

function closeModeWarningModal() {
    modeWarningModal.style.display = 'none';
}

function confirmModeChange() {
    const newMode = document.getElementById('mode').value;
    fetch('/change_mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode: newMode }),
    }).then(response => response.json())
      .then(data => {
          currentMode = newMode;
          updateModeDisplay(newMode);
          closeModeWarningModal();
      });
}

function updateModeDisplay(mode) {
    modeDisplay.textContent = mode;
    let color = '';
    switch (mode) {
        case 'setup':
            color = 'lightblue';
            break;
        case 'calibration':
            color = 'darkorange';
            break;
        case 'show':
            color = 'forestgreen';
            break;
        default:
            color = 'grey';
            break;
    }
    header.style.backgroundColor = color;
}

function updateAnchorsList() {
    const anchorsList = document.getElementById('anchors-list');
    anchorsList.innerHTML = '';
    fetch("/anchor_points")
        .then(response => response.json())
        .then(data => {
            data.anchor_points.forEach(anchor => {
                const li = document.createElement('li');
                li.textContent = `MAC: ${anchor.mac_address}, Name: ${anchor.user_defined_name || 'Unnamed'}, Location: ${anchor.user_defined_location || 'Unspecified'}`;
                anchorsList.appendChild(li);
            });
        }).catch(error => {
            addLog(`Failed to fetch anchor points: ${error}`);
        });
}

document.addEventListener('DOMContentLoaded', function() {
    showTab('devices');
    fetchMqttInfo();
    fetchLogs();
    fetchAnchorPoints();  // Fetch anchor points when the page loads

    fetch('/device_ids')
        .then(response => response.json())
        .then(data => {
            const deviceIdSelect = document.getElementById('device_id');
            const allOption = document.createElement('option');
            allOption.value = 'all';
            allOption.textContent = 'All';
            deviceIdSelect.appendChild(allOption);

            data.device_ids.forEach(device => {
                const option = document.createElement('option');
                option.value = device;
                option.textContent = device;
                deviceIdSelect.appendChild(option);
            });
        }).catch(error => {
            addLog(`Failed to fetch device IDs: ${error}`);
        });

    fetch('/get_mode')
        .then(response => response.json())
        .then(data => {
            currentMode = data.mode;
            updateModeDisplay(currentMode);
            document.getElementById('mode').value = currentMode; // Set the dropdown to the current mode
        });

    fetch('/anchor_macs')
        .then(response => response.json())
        .then(data => {
            const anchorMacSelect = document.getElementById('anchor_mac');
            data.anchor_macs.forEach(mac => {
                const option = document.createElement('option');
                option.value = mac;
                option.textContent = mac;
                anchorMacSelect.appendChild(option);
            });
        }).catch(error => {
            addLog(`Failed to fetch anchor MACs: ${error}`);
        });

    const ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onmessage = function(event) {
        const logsTbody = document.getElementById('logs-tbody');
        const logEntry = document.createElement('tr');
        const [timestamp, level, message] = parseLog(event.data);

        logEntry.innerHTML = `
            <td>${timestamp}</td>
            <td>${level}</td>
            <td>${message}</td>
        `;
        logsTbody.prepend(logEntry);
    };

    document.getElementById('wifiForm').onsubmit = function(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const configData = {
            device_id: formData.get('device_id'),
            ssid: formData.get('target_ssid'),
            password: formData.get('target_password')
        };
        fetch('/send_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(configData),
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => addLog(`WiFi configuration sent: ${JSON.stringify(configData)}`))
        .catch(error => addLog(`Failed to send configuration: ${error}`));
    };

    document.getElementById('anchor_mac').addEventListener('change', function() {
        const selectedMac = this.value.split(' - ')[0]; // Extract only the MAC address
        if (selectedMac !== "") {
            fetch(`/get_anchor_details/${selectedMac}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('anchor_name').value = data.user_defined_name || '';
                    document.getElementById('anchor_location').value = data.user_defined_location || '';
                }).catch(error => {
                    addLog(`Failed to fetch anchor details: ${error}`);
                });
        } else {
            document.getElementById('anchor_name').value = '';
            document.getElementById('anchor_location').value = '';
        }
    });

    document.getElementById('anchorForm').onsubmit = function(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const anchorUpdate = {
            mac_address: formData.get('anchor_mac').split(' - ')[0], // Extract only the MAC address
            user_defined_name: formData.get('anchor_name'),
            user_defined_location: formData.get('anchor_location')
        };
        fetch('/update_anchor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(anchorUpdate),
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => addLog(`Anchor updated: ${JSON.stringify(anchorUpdate)}`))
        .catch(error => addLog(`Failed to update anchor: ${error}`));
    };

    setInterval(fetchAnchorPoints, 5000); // Refresh every 5 seconds
});

function fetchLogs() {
    fetch('/logs')
        .then(response => response.json())
        .then(data => {
            const logsTbody = document.getElementById('logs-tbody');
            logsTbody.innerHTML = ''; // Clear existing logs
            data.logs.forEach(log => {
                if (log.level && log.message) {  // Only add valid log entries
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${log.timestamp}</td>
                        <td>${log.level}</td>
                        <td>${log.message}</td>
                    `;
                    logsTbody.appendChild(tr);
                }
            });
        }).catch(error => {
            addLog(`Failed to fetch logs: ${error}`);
        });
}

function fetchAnchorPoints() {
    console.log("Fetching anchor points...");
    fetch("/anchor_points")
        .then(response => response.json())
        .then(data => {
            const anchorContainer = document.getElementById("anchor-container");
            const anchorsList = document.getElementById("anchors-list");
            anchorContainer.innerHTML = "";  // Clear the container first
            anchorsList.innerHTML = ""; // Clear the list first
            data.anchor_points.forEach(anchor => {
                console.log("Anchor:", anchor);
                const img = document.createElement("img");
                img.src = "/static/images/anchor_ico.png";
                img.classList.add("anchor-icon");
                img.style.left = `${anchor.webpage_x}px`;
                img.style.top = `${anchor.webpage_y}px`;
                img.style.position = 'absolute';
                img.setAttribute("draggable", true);
                img.id = anchor.id;

                // Tooltip for anchor info
                const tooltip = document.createElement("div");
                tooltip.classList.add("anchor-tooltip");
                tooltip.innerHTML = `
                    ID: ${anchor.id}<br>
                    X: ${anchor.x_coordinate}<br>
                    Y: ${anchor.y_coordinate}<br>
                    Z: ${anchor.z_coordinate}<br>
                    Status: ${anchor.status}<br>
                    Last Updated: ${anchor.last_updated}<br>
                    Firmware: ${anchor.firmware_version}<br>
                    Name: ${anchor.user_defined_name}<br>
                    Location: ${anchor.user_defined_location}<br>
                    MAC: ${anchor.mac_address}<br>
                    IP: ${anchor.ip_address}
                `;

                img.appendChild(tooltip);
                img.addEventListener("dragstart", handleDragStart);
                img.addEventListener("dragend", handleDragEnd);
                anchorContainer.appendChild(img);

                const li = document.createElement('li');
                li.innerHTML = `
                    <strong>ID:</strong> ${anchor.id}<br>
                    <strong>Webpage X:</strong> ${anchor.webpage_x}<br>
                    <strong>Webpage Y:</strong> ${anchor.webpage_y}<br>
                    <strong>X Coordinate:</strong> ${anchor.x_coordinate}<br>
                    <strong>Y Coordinate:</strong> ${anchor.y_coordinate}<br>
                    <strong>Z Coordinate:</strong> ${anchor.z_coordinate}<br>
                    <strong>Status:</strong> ${anchor.status}<br>
                    <strong>Last Updated:</strong> ${anchor.last_updated}<br>
                    <strong>Firmware Version:</strong> ${anchor.firmware_version}<br>
                    <strong>Name:</strong> ${anchor.user_defined_name || 'Unnamed'}<br>
                    <strong>Location:</strong> ${anchor.user_defined_location || 'Unspecified'}<br>
                    <strong>MAC:</strong> ${anchor.mac_address}<br>
                    <strong>IP:</strong> ${anchor.ip_address}
                `;
                anchorsList.appendChild(li);
            });

            anchorContainer.addEventListener("dragover", handleDragOver);
            anchorContainer.addEventListener("drop", handleDrop);
        }).catch(error => {
            addLog(`Failed to fetch anchor points: ${error}`);
        });
}



function handleDragStart(event) {
    event.dataTransfer.setData('text/plain', event.target.id);
    event.target.classList.add('dragging');
}

function handleDragOver(event) {
    event.preventDefault();
    event.target.classList.add('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    const id = event.dataTransfer.getData('text/plain');
    const draggable = document.getElementById(id);
    event.target.classList.remove('drag-over');
    draggable.style.position = 'absolute';
    draggable.style.left = `${event.clientX - event.target.offsetLeft}px`;
    draggable.style.top = `${event.clientY - event.target.offsetTop}px`;

    // Save the new position to the database
    fetch('/update_anchor_position', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: id,
            webpage_x: event.clientX - event.target.offsetLeft,
            webpage_y: event.clientY - event.target.offsetTop
        }),
    }).then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => addLog(`Anchor position updated: ${JSON.stringify(data)}`))
    .catch(error => addLog(`Failed to update anchor position: ${error}`));
}

function handleDragEnd(event) {
    event.target.classList.remove('dragging');
}

function parseLog(log) {
    const [timestampPart, levelPart, ...messageParts] = log.split(' ');
    const timestamp = timestampPart;
    const level = levelPart.replace(/[\[\]]/g, '');
    const message = messageParts.join(' ');
    return [timestamp, level, message];
}
