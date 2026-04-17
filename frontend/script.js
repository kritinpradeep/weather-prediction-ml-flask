// frontend/script.js

// Load locations into dropdown on page load
window.onload = function () {
    fetch("http://127.0.0.1:5000/locations")
      .then(response => response.json())
      .then(locations => {
        const select = document.getElementById("location");
        locations.forEach(loc => {
          const option = document.createElement("option");
          option.value = loc;
          option.textContent = loc;
          select.appendChild(option);
        });
      });
  };
  
  function predict() {
    const location = document.getElementById("location").value;
  
    fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ location })
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          document.getElementById("result").innerHTML = `❌ ${data.error}`;
          return;
        }
  
        let html = `<h2>Next 24 Hours for ${location}</h2><table><tr><th>Time</th><th>Temperature (°C)</th><th>Humidity (%)</th><th>Wind Speed (km/h)</th><th>Precipitation (mm)</th></tr>`;
        data.forEach(entry => {
          html += `<tr><td>${entry.hour}</td><td>${entry.temperature}</td><td>${entry.humidity}</td><td>${entry.wind_speed}</td><td>${entry.precipitation}</td></tr>`;
        });
        html += "</table>";
        document.getElementById("result").innerHTML = html;
      })
      .catch(error => {
        document.getElementById("result").innerHTML = "⚠️ Error fetching prediction.";
        console.error("Error:", error);
      });
  }
  