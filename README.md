# 🏎️ F1 Telemetry Analysis Tool

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![FastF1](https://img.shields.io/badge/FastF1-3.3.6-E10600?style=for-the-badge&logo=f1&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Professional-grade Formula 1 race data intelligence platform.**  
Compare drivers, explore telemetry, analyze tyre strategy, and visualize G-forces — all in one dark-themed interactive dashboard.

![For the Test](https://f1-fanmade-telemetry-analysis-tool.streamlit.app)

</div>

---

## ✨ Features

| Tab | Feature |
|-----|---------|
| 🏆 **Race Hub** | Session results table with team colors, fastest laps, and driver summaries |
| 📊 **Telemetry** | Side-by-side speed, throttle, and brake traces with **Delta Time** analysis |
| 🛣️ **Racing Line & G-Force** | 2D track map overlay + Friction Circle (Lateral vs. Longitudinal G) |
| 🔥 **Heat Maps** | Track heat map colored by gear selection with distribution pie charts |
| 🔧 **Strategy & Tyres** | Stint Gantt chart + tyre degradation regression with fuel correction |

---

<details>
<summary>Click to expand</summary>

### 🏆 Race Results
Session standings with live team colors, best lap times, and points.

### 📊 Detailed Telemetry
Distance-based comparison of speed, throttle, and braking with delta time overlay.

### 🛣️ Racing Line & G-Force Friction Circle
Bird's-eye view of the track with both drivers' racing lines, alongside a classic friction circle diagram.

### 🔥 Gear Heat Map
Full track heat map showing which gear the driver uses at each section of the circuit.

### 🔧 Tyre Strategy
Horizontal Gantt chart for stint history + linear regression tyre degradation curves.

</details>

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/f1-telemetry-analysis-tool.git
cd f1-telemetry-analysis-tool

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

Then open your browser at `http://localhost:8501`.

> **Note:** The first data load for a session may take **1–2 minutes** as FastF1 downloads and caches the data. Subsequent loads are instant.

---

## 🕹️ Usage

1. **Select Season** — Choose a year from 2020 to the current season.
2. **Enter Grand Prix** — Type the GP name or country (e.g., `Bahrain`, `Monaco`, `British`).
3. **Choose Session** — Practice 1/2/3, Qualifying, Sprint, or Race.
4. **Enter Driver Codes** — Use standard 3-letter abbreviations (e.g., `VER`, `NOR`, `HAM`).
5. **Click 🚀 Load Telemetry** — All five tabs populate automatically.

---

## 📁 Project Structure

```
f1-telemetry-analysis-tool/
│
├── app.py              # Main Streamlit application (all logic & UI)
├── requirements.txt    # Python dependencies
├── cache/              # FastF1 local data cache (auto-created, gitignored)
└── README.md
```

---

## 🔬 Technical Details

### Delta Time
Uses `fastf1.utils.delta_time()` to compute the lap-time gap between two drivers at every distance point. Positive values indicate Driver 1 is behind; negative means Driver 1 is ahead.

### G-Force (Friction Circle)
- **Longitudinal G** — Derived from the rate of change of speed (m/s²) divided by 9.81.
- **Lateral G** — Computed from the heading angle change (`arctan2` of X/Y position deltas) multiplied by velocity.
- Values are clipped to a realistic ±5G range.

### Tyre Degradation
- Filters out in/out laps and inaccurate laps.
- Applies a **fuel correction** of ~0.065 s/lap to isolate true tyre degradation.
- Fits a **linear regression** to the corrected lap times and reports the degradation rate (s/lap).

### Color Resolution
Team colors are resolved in priority order:
1. FastF1 `results.TeamColor` field
2. Internal `F1_TEAM_COLORS` lookup table
3. `fastf1.plotting.driver_color()`
4. Fallback contrast palette (for visually similar colors)

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | 1.32.0 | Web dashboard framework |
| `fastf1` | 3.3.6 | F1 telemetry data API |
| `pandas` | latest | Data manipulation |
| `numpy` | latest | Numerical computation |
| `plotly` | latest | Interactive charts |
| `scipy` | latest | Statistical utilities |

---

## ⚠️ Data Availability

- Telemetry data is available from the **2018 season** onwards.
- Very recent races (within 24–48 hours) may have incomplete results (positions/times) — the app handles this gracefully and falls back to lap-time-based ranking.
- Some sessions (e.g., Sprint weekends) may not have all telemetry channels available.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [FastF1](https://github.com/theOehrly/Fast-F1) — The incredible library that makes F1 telemetry data accessible
- [Streamlit](https://streamlit.io/) — For making data apps delightfully simple to build
- [Plotly](https://plotly.com/) — For beautiful, interactive visualizations
- Formula 1® — All F1 data is property of Formula One World Championship Limited

---

<div align="center">
  Made with ❤️ and ☕ by a racing data enthusiast
</div>
