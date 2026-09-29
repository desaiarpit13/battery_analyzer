# 🔬 Detailed Line-by-Line Guide: `battery_engine.py`

This document provides a line-by-line and section-by-section breakdown of [`battery_engine.py`](file:///C:/Users/desai/Desktop/Batery%20Analyzer/battery_engine.py). This module represents the **computational core** of the Voltix Pro Battery Telemetry Suite, handling all electrochemical calculations, numerical integrations, cell health evaluations, and standalone HTML report generation.

---

## 1. Module Docstring & Standard Imports (Lines 1–12)

```python
1: """
2: Battery Analysis Engine
3: Core numerical calculations and analytical diagnostics for battery test telemetry.
4: """
```
* **Lines 1–4**: Module-level docstring describing the purpose of the engine.

```python
6: from dataclasses import dataclass, field
7: from typing import Dict, List, Optional, Tuple, Any
8: import os
9: import json
10: import numpy as np
11: import pandas as pd
```
* **Line 6**: Imports `dataclass` and `field` from Python's standard `dataclasses` module. `dataclass` automatically generates `__init__`, `__repr__`, and comparisons for clean data models. `field(default_factory=...)` allows initialization of mutable defaults (like lists).
* **Line 7**: Imports type hinting primitives (`Dict`, `List`, `Optional`, `Tuple`, `Any`) to ensure strict type safety.
* **Line 8**: Imports `os` for filesystem operations (path checking, basename extraction).
* **Line 9**: Imports `json` for serializing Python lists and dictionaries into JSON strings to inject telemetry data into Chart.js in the HTML report.
* **Line 10**: Imports `numpy` as `np` for fast vectorized numerical operations (differentiation, cumulative summation, arrays).
* **Line 11**: Imports `pandas` as `pd` for tabular telemetry handling (reading CSVs, columnar transformations, slicing).

---

## 2. Telemetry Metrics Data Model: `BatteryMetrics` (Lines 14–76)

The [`BatteryMetrics`](file:///C:/Users/desai/Desktop/Batery%20Analyzer/battery_engine.py#L14) dataclass serves as the centralized repository for all computed statistics of a test run.

```python
14: @dataclass
15: class BatteryMetrics:
```
* Decorates `BatteryMetrics` with `@dataclass`.

### Time Metrics (Lines 16–21)
```python
16:     # Time metrics
17:     duration_s: float = 0.0
18:     duration_min: float = 0.0
19:     data_points: int = 0
20:     sample_rate_s: float = 0.0
```
* **Line 17 (`duration_s`)**: Total duration of the discharge test in seconds ($t_{\text{end}} - t_{\text{start}}$).
* **Line 18 (`duration_min`)**: Total test duration in minutes (`duration_s / 60.0`).
* **Line 19 (`data_points`)**: Total number of sampled telemetry records ($N$).
* **Line 20 (`sample_rate_s`)**: Average time interval ($\Delta t$) between consecutive samples in seconds.

### Voltage Metrics (Lines 22–30)
```python
22:     # Voltage metrics
23:     v_initial: float = 0.0
24:     v_final: float = 0.0
25:     v_min: float = 0.0
26:     v_max: float = 0.0
27:     v_drop: float = 0.0
28:     v_mean: float = 0.0
29:     v_cutoff: float = 3.20
```
* **Line 23 (`v_initial`)**: Voltage at $t=0$ (initial open-circuit / loaded starting voltage).
* **Line 24 (`v_final`)**: Voltage at the final sample (terminal cutoff point).
* **Line 25 (`v_min`)**: Absolute minimum voltage recorded during the test.
* **Line 26 (`v_max`)**: Absolute maximum voltage recorded during the test.
* **Line 27 (`v_drop`)**: Total potential drop across the discharge ($\Delta V = V_{\text{initial}} - V_{\text{final}}$).
* **Line 28 (`v_mean`)**: Simple arithmetic mean of voltage across all points.
* **Line 29 (`v_cutoff`)**: Cutoff safety threshold set for this cell (defaults to $3.20\,\text{V}$).

### Current Metrics (Lines 31–38)
```python
31:     # Current metrics
32:     i_initial: float = 0.0
33:     i_final: float = 0.0
34:     i_min: float = 0.0
35:     i_max: float = 0.0
36:     i_mean: float = 0.0
37:     i_rms: float = 0.0
```
* **Line 32 (`i_initial`)**: Discharge current at test commencement ($A$).
* **Line 33 (`i_final`)**: Discharge current at test conclusion ($A$).
* **Line 34 (`i_min`)**: Minimum current draw observed ($A$).
* **Line 35 (`i_max`)**: Peak instantaneous current draw ($A$).
* **Line 36 (`i_mean`)**: Arithmetic mean current draw ($A$).
* **Line 37 (`i_rms`)**: Root-Mean-Square current ($I_{\text{rms}} = \sqrt{\frac{1}{N}\sum I_k^2}$), reflecting heating/thermal stress on internal conductors.

### Power Metrics (Lines 39–45)
```python
39:     # Power metrics
40:     p_initial: float = 0.0
41:     p_final: float = 0.0
42:     p_min: float = 0.0
43:     p_max: float = 0.0
44:     p_mean: float = 0.0
```
* **Lines 40–44**: Initial, final, minimum, peak, and average output power in Watts ($W = V \times I$).

### Capacity & Energy Metrics (Lines 46–54)
```python
46:     # Capacity & Energy metrics
47:     capacity_ah: float = 0.0
48:     capacity_mah: float = 0.0
49:     capacity_rect_ah: float = 0.0
50:     energy_wh: float = 0.0
51:     energy_mwh: float = 0.0
52:     energy_rect_wh: float = 0.0
53:     v_avg_discharge: float = 0.0  # Energy / Capacity
```
* **Line 47 (`capacity_ah`)**: Cumulative delivered capacity in Ampere-hours ($Ah$), computed via trapezoidal integration.
* **Line 48 (`capacity_mah`)**: Cumulative delivered capacity in milliampere-hours ($mAh$).
* **Line 49 (`capacity_rect_ah`)**: Cumulative capacity computed via simple rectangular sum (used for numerical accuracy benchmarks).
* **Line 50 (`energy_wh`)**: Cumulative delivered electrical energy in Watt-hours ($Wh$), computed via trapezoidal integration of $P(t)$.
* **Line 51 (`energy_mwh`)**: Delivered energy in milliwatt-hours ($mWh$).
* **Line 52 (`energy_rect_wh`)**: Cumulative energy computed via simple rectangular sum.
* **Line 53 (`v_avg_discharge`)**: Thermodynamic mean operating voltage:
  $$\bar{V}_{\text{discharge}} = \frac{\text{Energy (Wh)}}{\text{Capacity (Ah)}}$$

### Cell Health & Advanced Diagnostics (Lines 55–63)
```python
55:     # Cell Health & Advanced Diagnostics
56:     nominal_capacity_ah: float = 2.0
57:     c_rate_mean: float = 0.0
58:     c_rate_max: float = 0.0
59:     soh_pct: float = 0.0
60:     rdc_mean_mohm: float = 0.0
61:     rdc_median_mohm: float = 0.0
62:     rdc_final_mohm: float = 0.0
```
* **Line 56 (`nominal_capacity_ah`)**: Factory rated capacity against which health is evaluated ($Ah$).
* **Line 57 (`c_rate_mean`)**: Average discharge rate normalized to capacity ($C = I_{\text{mean}} / C_{\text{nom}}$).
* **Line 58 (`c_rate_max`)**: Maximum discharge C-rate experienced during testing.
* **Line 59 (`soh_pct`)**: State of Health percentage relative to nominal rating: $\text{SoH} = \min(100, (\text{Cap} / C_{\text{nom}}) \times 100)$.
* **Lines 60–62 (`rdc_*_mohm`)**: Mean, median, and final internal DC resistance ($R_{dc}$) in milliohms ($m\Omega$).

### Discharge Stage Diagnostics & Cell Rating (Lines 64–76)
```python
64:     # Discharge Stage Diagnostics
65:     ohmic_drop_v: float = 0.0
66:     plateau_v_mean: float = 0.0
67:     plateau_duration_s: float = 0.0
68:     knee_voltage: float = 0.0
69:     knee_time_s: float = 0.0
70:     max_sag_rate_mv_s: float = 0.0
71: 
72:     # Cell Rating
73:     cell_grade: str = "Grade A"
74:     cell_status_summary: str = ""
75:     warnings: List[str] = field(default_factory=list)
```
* **Line 65 (`ohmic_drop_v`)**: Instantaneous voltage drop upon initial load application ($V_0 - V_1$).
* **Lines 66–67 (`plateau_*`)**: Average voltage and duration of the stable discharge phase ($3.6\,\text{V} \le V \le 4.0\,\text{V}$).
* **Lines 68–69 (`knee_*`)**: Voltage and timestamp at which the discharge curve enters rapid depletion ($V \le 3.5\,\text{V}$).
* **Line 70 (`max_sag_rate_mv_s`)**: Peak rate of voltage collapse $|dV/dt|$ ($mV/s$).
* **Lines 73–75**: Health rating tier (`Grade A`, `Grade B`, `Grade C`), descriptive summary, and list of safety warning messages.

---

## 3. Telemetry Processing Pipeline: `BatteryDataset` (Lines 78–284)

```python
78: class BatteryDataset:
79:     """Represents a battery dataset with raw data, processed telemetry, and diagnostics."""
80: 
81:     def __init__(self, df: pd.DataFrame, source_name: str = "Unknown", nominal_capacity_ah: float = 2.0, cutoff_voltage: float = 3.2):
82:         self.source_name = source_name
83:         self.nominal_capacity_ah = nominal_capacity_ah
84:         self.cutoff_voltage = cutoff_voltage
85:         self.df = df.copy()
86:         self.metrics = BatteryMetrics()
87:         self.process_data()
```
* **Lines 81–87**: Constructor takes raw DataFrame `df`, stores metadata, makes a defensive copy with `df.copy()`, instantiates `self.metrics = BatteryMetrics()`, and immediately runs `self.process_data()`.

### `process_data()`: Column Normalization & Cleansing (Lines 89–119)
```python
91:         df = self.df
92: 
93:         # Ensure required columns exist
94:         col_map = {}
95:         for col in df.columns:
96:             clow = str(col).strip().lower()
97:             if "time" in clow or "t(" in clow or "sec" in clow:
98:                 col_map[col] = "Time"
99:             elif "volt" in clow or "v(" in clow or clow == "v":
100:                 col_map[col] = "Voltage"
101:             elif "curr" in clow or "amp" in clow or "i(" in clow or clow == "i":
102:                 col_map[col] = "Current"
103: 
104:         if col_map:
105:             df.rename(columns=col_map, inplace=True)
```
* **Lines 94–105**: Flexible column name mapper. Accepts variations like `Time (s)`, `time`, `Voltage (V)`, `V`, `Current (A)`, `Amp`, etc., and standardizes them into `["Time", "Voltage", "Current"]`.

```python
107:         for req in ["Time", "Voltage", "Current"]:
108:             if req not in df.columns:
109:                 raise ValueError(f"Required column '{req}' not found in dataset. Found columns: {list(df.columns)}")
110: 
111:         # Convert to numeric
112:         df["Time"] = pd.to_numeric(df["Time"], errors="coerce").fillna(0.0)
113:         df["Voltage"] = pd.to_numeric(df["Voltage"], errors="coerce").fillna(0.0)
114:         df["Current"] = pd.to_numeric(df["Current"], errors="coerce").fillna(0.0)
115: 
116:         # Sort by Time just in case
117:         df.sort_values(by="Time", inplace=True)
118:         df.reset_index(drop=True, inplace=True)
```
* **Lines 107–109**: Validates that all 3 canonical channels exist, raising a informative error if missing.
* **Lines 112–114**: Coerces channels to float numbers, replacing non-numeric corrupted entries with `0.0`.
* **Lines 117–118**: Enforces monotonic chronological ordering and resets DataFrame indexing.

### `process_data()`: Time Differences & Numerical Integration (Lines 120–150)
```python
120:         # Time difference
121:         t = df["Time"].to_numpy(dtype=float)
122:         v = df["Voltage"].to_numpy(dtype=float)
123:         i = df["Current"].to_numpy(dtype=float)
124:         n = len(t)
125: 
126:         if n < 2:
127:             raise ValueError("Dataset must contain at least 2 data points.")
128: 
129:         dt = np.zeros(n)
130:         dt[1:] = np.diff(t)
131:         df["dt"] = dt
```
* **Lines 121–124**: Extracts channels as high-speed NumPy arrays.
* **Lines 126–127**: Ensures dataset contains at least 2 points to permit differentiation/integration.
* **Lines 129–131**: Computes interval array $\Delta t_k = t_k - t_{k-1}$ using `np.diff(t)`.

```python
133:         # Instantaneous Power (W)
134:         p = v * i
135:         df["Power"] = p
136: 
137:         # Rectangular integration
138:         df["Capacity_Rect_Ah"] = (i * dt).cumsum() / 3600.0
139:         df["Energy_Rect_Wh"] = (p * dt).cumsum() / 3600.0
140: 
141:         # Trapezoidal integration (High Precision)
142:         cap_trap = np.zeros(n)
143:         cap_trap[1:] = np.cumsum(0.5 * (i[1:] + i[:-1]) * dt[1:]) / 3600.0
144:         df["Capacity_Ah"] = cap_trap
145:         df["Capacity_mAh"] = cap_trap * 1000.0
146: 
147:         energy_trap = np.zeros(n)
148:         energy_trap[1:] = np.cumsum(0.5 * (p[1:] + p[:-1]) * dt[1:]) / 3600.0
149:         df["Energy_Wh"] = energy_trap
150:         df["Energy_mWh"] = energy_trap * 1000.0
```
* **Lines 134–135**: Vectorized element-wise instantaneous electrical power $P_k = V_k \times I_k$.
* **Lines 138–139**: Rectangular cumulative capacity $\sum I_k \Delta t_k / 3600$ and energy $\sum P_k \Delta t_k / 3600$.
* **Lines 142–150**: High-precision trapezoidal numerical integration using:
  $$\text{Cap}(t) = \frac{1}{3600} \sum_{k=1}^n \frac{I_k + I_{k-1}}{2} \Delta t_k$$
  and
  $$\text{Energy}(t) = \frac{1}{3600} \sum_{k=1}^n \frac{P_k + P_{k-1}}{2} \Delta t_k$$
  Calculated across the entire vector in microseconds via vectorized slicing `i[1:] + i[:-1]`.

### `process_data()`: SoC, C-Rate, Sag Velocity & DC Internal Resistance (Lines 152–186)
```python
152:         total_cap = cap_trap[-1]
153:         total_energy = energy_trap[-1]
154: 
155:         # State of Charge (SoC %) based on Coulomb counting
156:         if total_cap > 1e-6:
157:             df["SoC_pct"] = np.clip(100.0 * (1.0 - (cap_trap / total_cap)), 0.0, 100.0)
158:         else:
159:             df["SoC_pct"] = 100.0
160: 
161:         # C-rate profile
162:         nom_cap = max(self.nominal_capacity_ah, 0.01)
163:         df["C_Rate"] = i / nom_cap
164: 
165:         # Voltage Sag Rate (dV/dt) in mV/s
166:         dv = np.zeros(n)
167:         dv[1:] = np.diff(v)
168:         dt_safe = np.where(dt <= 0, 1.0, dt)
169:         dv_dt = np.zeros(n)
170:         dv_dt[1:] = (dv[1:] / dt_safe[1:]) * 1000.0  # mV / s
171:         df["dV_dt_mV_s"] = dv_dt
```
* **Lines 156–159**: Coulomb-counting State of Charge (SoC %):
  $$\text{SoC}(t) = 100 \times \left(1 - \frac{\text{Cap}(t)}{\text{Cap}_{\text{total}}}\right)$$
* **Lines 162–163**: Instantaneous C-rate: $I(t) / C_{\text{nom}}$.
* **Lines 166–171**: Computes voltage sag derivative $dV/dt$ scaled to $mV/s$, protecting against zero-division with `np.where(dt <= 0, 1.0, dt)`.

```python
173:         # DC Internal Resistance (R_dc) estimation
174:         di = np.zeros(n)
175:         di[1:] = np.diff(i)
176:         rdc_arr = np.zeros(n)
177:         valid_steps = np.abs(di) >= 0.025  # step change threshold
178:         for idx in range(1, n):
179:             if valid_steps[idx]:
180:                 rdc_arr[idx] = (abs(dv[idx]) / abs(di[idx])) * 1000.0  # mOhm
181:             else:
182:                 rdc_arr[idx] = rdc_arr[idx - 1] if idx > 1 else 0.0
183:         df["R_dc_mOhm"] = rdc_arr
184: 
185:         # Store updated dataframe
186:         self.df = df
```
* **Lines 173–183**: Estimates dynamic internal resistance $R_{dc}$. Detects step changes in discharge current $|\Delta I| \ge 25\,\text{mA}$, calculating:
  $$R_{dc} = \frac{|\Delta V|}{|\Delta I|} \times 1000 \quad [m\Omega]$$
  and carrying forward the most recent valid impedance value across steady-state samples.

### `process_data()`: Summary Aggregations & Stage Breakdown (Lines 189–264)
```python
189:         # Compute summary metrics
190:         m = self.metrics
191:         m.duration_s = float(t[-1] - t[0])
...
208:         m.i_rms = float(np.sqrt(np.mean(i**2)))
...
223:         m.v_avg_discharge = float(total_energy / total_cap) if total_cap > 1e-6 else m.v_mean
228:         m.soh_pct = float(min(100.0, (total_cap / nom_cap) * 100.0))
```
* **Lines 190–240**: Aggregates min, max, mean, RMS, and median statistics onto `self.metrics`.
* **Lines 242–264**: Discharge stage detection:
  * `ohmic_drop_v`: Initial step drop between the first two data points ($V_0 - V_1$).
  * `plateau_v_mean` & `plateau_duration_s`: Slices the region where $3.6\,\text{V} \le V \le 4.0\,\text{V}$ to identify the primary working plateau.
  * `knee_voltage` & `knee_time_s`: Finds the first point where voltage drops below $3.5\,\text{V}$ (the onset of the depletion knee).
  * `max_sag_rate_mv_s`: Maximum $|dV/dt|$ observed during discharge.

### `process_data()`: Diagnostics, Safety Warnings & Cell Grading (Lines 266–284)
```python
266:         m.warnings = []
267:         if m.v_final < self.cutoff_voltage:
268:             m.warnings.append(f"Cutoff voltage breached: {m.v_final:.2f}V is below safe limit ({self.cutoff_voltage:.2f}V).")
269:         if m.max_sag_rate_mv_s > 15.0:
270:             m.warnings.append(f"High voltage sag rate observed ({m.max_sag_rate_mv_s:.1f} mV/s).")
271:         if m.c_rate_max > 2.0:
272:             m.warnings.append(f"Peak discharge C-rate exceeded 2.0C ({m.c_rate_max:.2f}C).")
273: 
274:         # Grade assignment
275:         if m.soh_pct >= 90.0 and m.rdc_median_mohm < 350.0:
276:             m.cell_grade = "Grade A (Prime)"
277:             m.cell_status_summary = "Optimal cell health, low internal impedance, and excellent energy delivery."
278:         elif m.soh_pct >= 75.0 or m.rdc_median_mohm < 500.0:
279:             m.cell_grade = "Grade B (Good)"
280:             m.cell_status_summary = "Healthy operational cell with moderate impedance rise; suitable for normal duty."
281:         else:
282:             m.cell_grade = "Grade C (Degraded)"
283:             m.cell_status_summary = "Significant capacity fade or elevated resistance; recommend cycling or retirement."
```
* **Lines 266–273**: Checks for safety anomalies (cutoff undervoltage, excessive voltage collapse $> 15\,\text{mV/s}$, or discharge rate $> 2.0\text{C}$).
* **Lines 275–284**: Automated three-tier cell classification:
  * **Grade A (Prime)**: $\ge 90\%$ capacity retention and $R_{dc} < 350\,m\Omega$.
  * **Grade B (Good)**: $\ge 75\%$ retention or $R_{dc} < 500\,m\Omega$.
  * **Grade C (Degraded)**: $< 75\%$ retention and elevated impedance.

---

## 4. Factory Helper: `load_and_analyze()` (Lines 286–292)

```python
286: def load_and_analyze(file_path: str, nominal_capacity_ah: float = 2.0, cutoff_voltage: float = 3.2) -> BatteryDataset:
287:     """Loads a CSV file and runs full analysis."""
288:     if not os.path.exists(file_path):
289:         raise FileNotFoundError(f"File not found: {file_path}")
290:     df = pd.read_csv(file_path)
291:     base_name = os.path.basename(file_path)
292:     return BatteryDataset(df, source_name=base_name, nominal_capacity_ah=nominal_capacity_ah, cutoff_voltage=cutoff_voltage)
```
* **Lines 286–292**: Convenience utility. Validates that `file_path` exists on disk, parses it using `pd.read_csv`, extracts the file's basename, and returns a fully initialized and computed `BatteryDataset`.

---

## 5. Web Dashboard Export: `export_html_report()` (Lines 295–602)

```python
295: def export_html_report(battery: BatteryDataset, output_path: str) -> str:
296:     """Generates an executive, dark-themed interactive HTML report with Chart.js visualization."""
```
* **Lines 297–314**: Subsamples the telemetry data (downsampling to a maximum of 80 evenly distributed points using `df.iloc[::step]`) so that the generated browser report remains lightweight and renders instantly. Converts data vectors to pure Python lists for JSON encoding.
* **Lines 316–375**: Injects responsive CSS3 styles:
  * Dark engineering theme with CSS custom properties (`--bg-main: #0b0f17`, `--cyan: #00e5ff`, etc.).
  * Glassmorphism cards and CSS Grid layouts (`.kpi-grid`, `.chart-grid`).
* **Lines 378–483**: Generates HTML markup:
  * Header with cell grade badge.
  * Diagnostic alert callout (only rendered if warnings exist).
  * 5 KPI summary cards.
  * 4 Chart.js canvas elements (`voltageChart`, `currentPowerChart`, `capacityChart`, `socChart`).
  * Comprehensive analytical telemetry data table.
* **Lines 485–595**: Client-side JavaScript using Chart.js:
  * Sets up responsive dark-themed axes, grids, and tooltips.
  * Dual-axis line chart for simultaneous Current ($A$) and Power ($W$) monitoring with independent $y$-scales.
* **Lines 599–601**: Writes the HTML content to disk using UTF-8 encoding and returns the destination path.
