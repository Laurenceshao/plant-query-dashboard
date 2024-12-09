<template>
  <div class="app">
    <h1 class="title">Plant Query Dashboard</h1>
    <textarea
      v-model="query"
      placeholder="Ask about your plant..."
      class="textarea"
    ></textarea>
    <button @click="submitQuery" class="button">Submit</button>
    <div v-if="response" class="response">
      <p>{{ response }}</p>
    </div>
    <div class="canvas-container">
      <canvas id="sensorChart" class="chart-canvas"></canvas>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { Chart, registerables } from "chart.js";
import Trianglify from "trianglify";

export default {
  data() {
    return {
      query: "",
      response: "",
    };
  },
  methods: {
    async submitQuery() {
      try {
        const res = await axios.post(
          "http://130.126.136.105:7999/api/process_text/",
          {
            text: this.query,
          }
        );
        this.response = res.data.response || "No response available.";
      } catch (error) {
        console.error("API Error:", error);
        this.response = "Error: Could not fetch the response.";
      }
    },
    async fetchSensorData() {
      try {
        const res = await axios.get(
          "http://130.126.136.105:7999/api/sensor_data/"
        );
        return res.data;
      } catch (error) {
        console.error("Error fetching sensor data:", error);
        return [];
      }
    },
    async renderChart() {
      const data = await this.fetchSensorData();
      if (data.length === 0) return;

      Chart.register(...registerables);

      const ctx = document.getElementById("sensorChart");
      if (!ctx) {
        console.error("Canvas element not found");
        return;
      }

      const timestamps = data.map((item) =>
        new Date(item.timestamp).toLocaleTimeString()
      );
      const moisture = data.map((item) => (item.moisture - 20) / 20); // normalize
      const temperature = data.map((item) => item.temperature);
      const lightIntensity = data.map((item) => item.light_intensity);

      new Chart(ctx, {
        type: "line",
        data: {
          labels: timestamps,
          datasets: [
            {
              label: "Moisture (%)",
              data: moisture,
              borderColor: "rgba(56, 136, 255, 1)",
              backgroundColor: "rgba(56, 136, 255, 0.2)",
              fill: true,
            },
            {
              label: "Temperature (°C)",
              data: temperature,
              borderColor: "rgba(255, 99, 132, 1)",
              backgroundColor: "rgba(255, 99, 132, 0.2)",
              fill: true,
            },
            {
              label: "Light Intensity (Average Pixel Intensity)",
              data: lightIntensity,
              borderColor: "rgba(255, 206, 86, 1)",
              backgroundColor: "rgba(255, 206, 86, 0.2)",
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            x: { title: { display: true, text: "Timestamp" } },
            y: { title: { display: true, text: "Value" } },
          },
        },
      });
    },
  },
  mounted() {
    // Generate background
    const generateBackground = () => {
      const pattern = Trianglify({
        width: window.innerWidth,
        height: window.innerHeight,
        cellSize: 80,
        xColors: ["#2e7d32", "#66bb6a", "#a5d6a7", "#c8e6c9", "#e8f5e9"],
      });

      const canvas = pattern.toCanvas();
      canvas.style.position = "absolute";
      canvas.style.top = "0";
      canvas.style.left = "0";
      canvas.style.width = "100%";
      canvas.style.height = "100%";
      canvas.style.zIndex = "-1";

      const oldCanvas = document.querySelector("canvas.background");
      if (oldCanvas) {
        document.body.replaceChild(canvas, oldCanvas);
      } else {
        canvas.classList.add("background");
        document.body.appendChild(canvas);
      }
    };

    generateBackground();
    window.addEventListener("resize", generateBackground);

    // Render chart
    this.renderChart();
  },
};
</script>

<style>
body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: Arial, sans-serif;
}

.app {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 100vh;
  text-align: center;
  position: relative;
  z-index: 1;
}

.dashboard {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  width: 300px;
}

.title {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 15px;
}

.textarea {
  width: 100%;
  height: 100px;
  margin-bottom: 10px;
  padding: 10px;
  font-size: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #222;
  color: #fff;
}

.button {
  width: 100%;
  padding: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}

.button:hover {
  background-color: #45a049;
}

.response {
  margin-top: 10px;
  text-align: left;
  color: #333;
  font-size: 0.9rem;
}

.visualization-container {
  flex-grow: 1;
  width: 90%;
  max-width: 1200px;
  margin-top: 200px;
}

.chart-canvas {
  width: 100%;
  height: 400px;
}
</style>

