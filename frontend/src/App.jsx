import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";


import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  };

  const analyzeMRI = async () => {
    if (!file) {
      alert("Please select an MRI image");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      const response = await axios.post(
        "http://127.0.0.1:5000/predict",
        formData,
      );
      console.log(response.data);
      setResult(response.data);
      fetchHistory();
    } catch (error) {
      console.error(error);
      alert("Prediction Failed");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    if (!risk) return "#38bdf8";

    if (risk.toLowerCase() === "high") {
      return "#ef4444";
    }

    if (risk.toLowerCase() === "medium") {
      return "#f59e0b";
    }

    return "#22c55e";
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/history");

      setHistory(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  const chartData = {};

  history.forEach((item) => {
    chartData[item.prediction] = (chartData[item.prediction] || 0) + 1;
  });

  const pieData = Object.keys(chartData).map((key) => ({
    name: key,
    value: chartData[key],
  }));

  const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444"];

  return (
    <div className="container">
      <div className="hero">
        <h1>🧠 Brain Tumor AI</h1>

        <p>
          MRI Classification, Grad-CAM Visualization & Medical Risk Assessment
        </p>
      </div>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>83.5%</h3>
          <p>Model Accuracy</p>
        </div>

        <div className="stat-card">
          <h3>4</h3>
          <p>Tumor Classes</p>
        </div>

        <div className="stat-card">
          <h3>EfficientNetB0</h3>
          <p>Model</p>
        </div>

        <div className="stat-card">
          <h3>Grad-CAM</h3>
          <p>Explainable AI</p>
        </div>
      </div>

      <div className="upload-card">
        <h2>Upload MRI Scan</h2>

        <label className="upload-box">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            hidden
          />

          <div className="upload-content">
            <div className="upload-icon">🧠</div>

            <h3>Select MRI Image</h3>

            <p>JPG, JPEG or PNG files</p>

            {file && <span className="file-name">{file.name}</span>}
          </div>
        </label>

        {preview && <img src={preview} alt="MRI Preview" className="preview" />}

        <button className="analyze-btn" onClick={analyzeMRI}>
          Analyze MRI
        </button>
      </div>

      {loading && (
        <div className="loading-card">
          <h2>Analyzing MRI...</h2>
        </div>
      )}

      {result && (
        <div className="result-card">
          <h2>Prediction Results</h2>

          <div className="summary-grid">
            <div className="card">
              <h4>Tumor Type</h4>
              <p>{result.prediction}</p>
            </div>

            <div className="card">
              <h4>Confidence</h4>
              <p>{result.confidence}%</p>
            </div>
          </div>

          <div className="medical-card">
            <h3>Medical Assessment</h3>

            <div className="assessment-row">
              <strong>Grad-CAM ROI Area:</strong>
              <span>{result.tumor_area}%</span>
            </div>

            <div className="assessment-row">
              <span>Risk Level</span>

              <span
                style={{
                  color: getRiskColor(result.risk_level),
                  fontWeight: "bold",
                }}
              >
                {result.risk_level}
              </span>
            </div>

            <div className="assessment-row">
              <span>Recommendation</span>
              <span>{result.recommendation}</span>
            </div>
          </div>

          <div className="knowledge-card">
            <h3>Tumor Information</h3>

            <div className="assessment-row">
              <span>Description</span>
              <span>{result.description}</span>
            </div>

            <div className="assessment-row">
              <span>Survival Rate</span>
              <span>{result.survival_rate}</span>
            </div>

            <div className="assessment-row">
              <span>Treatment</span>
              <span>{result.treatment}</span>
            </div>

            <div className="assessment-row">
              <span>Specialist</span>
              <span>{result.specialist}</span>
            </div>

            <div className="assessment-row">
              <span>Operation Possibility</span>
              <span>{result.operation}</span>
            </div>
          </div>

          {result.heatmap && (
            <div className="heatmap-card">
              <h3>Grad-CAM Visualization</h3>

              <img src={result.heatmap} alt="GradCAM" className="heatmap" />
            </div>
          )}

          <div className="probability-section">
            <h3>Class Probabilities</h3>

            {result.probabilities &&
              Object.entries(result.probabilities).map(([key, value]) => (
                <div key={key} className="probability-card">
                  <div className="prob-header">
                    <span>{key}</span>

                    <span>{value}%</span>
                  </div>

                  <div className="progress">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${value}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
          </div>

          {result.report && (
            <a href={result.report} target="_blank" rel="noreferrer">
              <button className="download-btn">Download PDF Report</button>
            </a>
          )}
        </div>
      )}

      {history.length > 0 && (
        <div className="history-card">
          <h2>Prediction History</h2>

          <table className="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Prediction</th>
                <th>Confidence</th>
                <th>Risk</th>
              </tr>
            </thead>

            <tbody>
              {history
                .slice()
                .reverse()
                .map((item, index) => (
                  <tr key={index}>
                    <td>{item.date}</td>

                    <td>{item.prediction}</td>

                    <td>{item.confidence}%</td>

                    <td>{item.risk}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}

      {history.length > 0 && (
        <div className="analytics-card">
          <h2>Analytics Dashboard</h2>

          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={120}
                dataKey="value"
                nameKey="name"
                label
              >
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>

              <Tooltip />

              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default App;
