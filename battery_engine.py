"""
Battery Analysis Engine
Core numerical calculations and analytical diagnostics for battery test telemetry.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import os
import json
import numpy as np
import pandas as pd


@dataclass
class BatteryMetrics:
    # Time metrics
    duration_s: float = 0.0
    duration_min: float = 0.0
    data_points: int = 0
    sample_rate_s: float = 0.0

    # Voltage metrics
    v_initial: float = 0.0
    v_final: float = 0.0
    v_min: float = 0.0
    v_max: float = 0.0
    v_drop: float = 0.0
    v_mean: float = 0.0
    v_cutoff: float = 3.20

    # Current metrics
    i_initial: float = 0.0
    i_final: float = 0.0
    i_min: float = 0.0
    i_max: float = 0.0
    i_mean: float = 0.0
    i_rms: float = 0.0

    # Power metrics
    p_initial: float = 0.0
    p_final: float = 0.0
    p_min: float = 0.0
    p_max: float = 0.0
    p_mean: float = 0.0

    # Capacity & Energy metrics
    capacity_ah: float = 0.0
    capacity_mah: float = 0.0
    capacity_rect_ah: float = 0.0
    energy_wh: float = 0.0
    energy_mwh: float = 0.0
    energy_rect_wh: float = 0.0
    v_avg_discharge: float = 0.0  # Energy / Capacity

    # Cell Health & Advanced Diagnostics
    nominal_capacity_ah: float = 2.0
    c_rate_mean: float = 0.0
    c_rate_max: float = 0.0
    soh_pct: float = 0.0
    rdc_mean_mohm: float = 0.0
    rdc_median_mohm: float = 0.0
    rdc_final_mohm: float = 0.0

    # Discharge Stage Diagnostics
    ohmic_drop_v: float = 0.0
    plateau_v_mean: float = 0.0
    plateau_duration_s: float = 0.0
    knee_voltage: float = 0.0
    knee_time_s: float = 0.0
    max_sag_rate_mv_s: float = 0.0

    # Cell Rating
    cell_grade: str = "Grade A"
    cell_status_summary: str = ""
    warnings: List[str] = field(default_factory=list)


class BatteryDataset:
    """Represents a battery dataset with raw data, processed telemetry, and diagnostics."""

    def __init__(self, df: pd.DataFrame, source_name: str = "Unknown", nominal_capacity_ah: float = 2.0, cutoff_voltage: float = 3.2):
        self.source_name = source_name
        self.nominal_capacity_ah = nominal_capacity_ah
        self.cutoff_voltage = cutoff_voltage
        self.df = df.copy()
        self.metrics = BatteryMetrics()
        self.process_data()

    def process_data(self):
        """Perform comprehensive battery calculation pipeline."""
        df = self.df

        # Ensure required columns exist
        col_map = {}
        for col in df.columns:
            clow = str(col).strip().lower()
            if "time" in clow or "t(" in clow or "sec" in clow:
                col_map[col] = "Time"
            elif "volt" in clow or "v(" in clow or clow == "v":
                col_map[col] = "Voltage"
            elif "curr" in clow or "amp" in clow or "i(" in clow or clow == "i":
                col_map[col] = "Current"

        if col_map:
            df.rename(columns=col_map, inplace=True)

        for req in ["Time", "Voltage", "Current"]:
            if req not in df.columns:
                raise ValueError(f"Required column '{req}' not found in dataset. Found columns: {list(df.columns)}")

        # Convert to numeric
        df["Time"] = pd.to_numeric(df["Time"], errors="coerce").fillna(0.0)
        df["Voltage"] = pd.to_numeric(df["Voltage"], errors="coerce").fillna(0.0)
        df["Current"] = pd.to_numeric(df["Current"], errors="coerce").fillna(0.0)

        # Sort by Time just in case
        df.sort_values(by="Time", inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Time difference
        t = df["Time"].to_numpy(dtype=float)
        v = df["Voltage"].to_numpy(dtype=float)
        i = df["Current"].to_numpy(dtype=float)
        n = len(t)

        if n < 2:
            raise ValueError("Dataset must contain at least 2 data points.")

        dt = np.zeros(n)
        dt[1:] = np.diff(t)
        df["dt"] = dt

        # Instantaneous Power (W)
        p = v * i
        df["Power"] = p

        # Rectangular integration
        df["Capacity_Rect_Ah"] = (i * dt).cumsum() / 3600.0
        df["Energy_Rect_Wh"] = (p * dt).cumsum() / 3600.0

        # Trapezoidal integration (High Precision)
        cap_trap = np.zeros(n)
        cap_trap[1:] = np.cumsum(0.5 * (i[1:] + i[:-1]) * dt[1:]) / 3600.0
        df["Capacity_Ah"] = cap_trap
        df["Capacity_mAh"] = cap_trap * 1000.0

        energy_trap = np.zeros(n)
        energy_trap[1:] = np.cumsum(0.5 * (p[1:] + p[:-1]) * dt[1:]) / 3600.0
        df["Energy_Wh"] = energy_trap
        df["Energy_mWh"] = energy_trap * 1000.0

        total_cap = cap_trap[-1]
        total_energy = energy_trap[-1]

        # State of Charge (SoC %) based on Coulomb counting
        if total_cap > 1e-6:
            df["SoC_pct"] = np.clip(100.0 * (1.0 - (cap_trap / total_cap)), 0.0, 100.0)
        else:
            df["SoC_pct"] = 100.0

        # C-rate profile
        nom_cap = max(self.nominal_capacity_ah, 0.01)
        df["C_Rate"] = i / nom_cap

        # Voltage Sag Rate (dV/dt) in mV/s
        dv = np.zeros(n)
        dv[1:] = np.diff(v)
        dt_safe = np.where(dt <= 0, 1.0, dt)
        dv_dt = np.zeros(n)
        dv_dt[1:] = (dv[1:] / dt_safe[1:]) * 1000.0  # mV / s
        df["dV_dt_mV_s"] = dv_dt

        # DC Internal Resistance (R_dc) estimation
        di = np.zeros(n)
        di[1:] = np.diff(i)
        rdc_arr = np.zeros(n)
        valid_steps = np.abs(di) >= 0.025  # step change threshold
        for idx in range(1, n):
            if valid_steps[idx]:
                rdc_arr[idx] = (abs(dv[idx]) / abs(di[idx])) * 1000.0  # mOhm
            else:
                rdc_arr[idx] = rdc_arr[idx - 1] if idx > 1 else 0.0
        df["R_dc_mOhm"] = rdc_arr

        # Store updated dataframe
        self.df = df

        # Compute summary metrics
        m = self.metrics
        m.duration_s = float(t[-1] - t[0])
        m.duration_min = m.duration_s / 60.0
        m.data_points = n
        m.sample_rate_s = float(np.mean(dt[1:])) if n > 1 else 0.0

        m.v_initial = float(v[0])
        m.v_final = float(v[-1])
        m.v_min = float(np.min(v))
        m.v_max = float(np.max(v))
        m.v_drop = float(m.v_initial - m.v_final)
        m.v_mean = float(np.mean(v))
        m.v_cutoff = float(self.cutoff_voltage)

        m.i_initial = float(i[0])
        m.i_final = float(i[-1])
        m.i_min = float(np.min(i))
        m.i_max = float(np.max(i))
        m.i_mean = float(np.mean(i))
        m.i_rms = float(np.sqrt(np.mean(i**2)))

        m.p_initial = float(p[0])
        m.p_final = float(p[-1])
        m.p_min = float(np.min(p))
        m.p_max = float(np.max(p))
        m.p_mean = float(np.mean(p))

        m.capacity_ah = float(total_cap)
        m.capacity_mah = float(total_cap * 1000.0)
        m.capacity_rect_ah = float(df["Capacity_Rect_Ah"].iloc[-1])
        m.energy_wh = float(total_energy)
        m.energy_mwh = float(total_energy * 1000.0)
        m.energy_rect_wh = float(df["Energy_Rect_Wh"].iloc[-1])

        m.v_avg_discharge = float(total_energy / total_cap) if total_cap > 1e-6 else m.v_mean

        m.nominal_capacity_ah = float(self.nominal_capacity_ah)
        m.c_rate_mean = float(m.i_mean / nom_cap)
        m.c_rate_max = float(m.i_max / nom_cap)
        m.soh_pct = float(min(100.0, (total_cap / nom_cap) * 100.0))

        # Filtered IR metrics
        valid_ir = rdc_arr[rdc_arr > 0]
        if len(valid_ir) > 0:
            m.rdc_mean_mohm = float(np.mean(valid_ir))
            m.rdc_median_mohm = float(np.median(valid_ir))
            m.rdc_final_mohm = float(valid_ir[-1])
        else:
            m.rdc_mean_mohm = 0.0
            m.rdc_median_mohm = 0.0
            m.rdc_final_mohm = 0.0

        # Stage analysis
        m.ohmic_drop_v = float(v[0] - v[1]) if n > 1 else 0.0

        # Plateau detection: region where 3.6V <= V <= 4.0V
        plateau_mask = (v >= 3.6) & (v <= 4.0)
        if np.any(plateau_mask):
            m.plateau_v_mean = float(np.mean(v[plateau_mask]))
            m.plateau_duration_s = float(np.sum(dt[plateau_mask]))
        else:
            m.plateau_v_mean = m.v_mean
            m.plateau_duration_s = m.duration_s * 0.7

        # Knee detection: point where discharge curve steepens (V <= 3.5V)
        knee_indices = np.where(v <= 3.5)[0]
        if len(knee_indices) > 0:
            k_idx = knee_indices[0]
            m.knee_voltage = float(v[k_idx])
            m.knee_time_s = float(t[k_idx])
        else:
            m.knee_voltage = float(v[-1])
            m.knee_time_s = float(t[-1])

        m.max_sag_rate_mv_s = float(np.max(np.abs(dv_dt)))

        # Diagnostics & Grading
        m.warnings = []
        if m.v_final < self.cutoff_voltage:
            m.warnings.append(f"Cutoff voltage breached: {m.v_final:.2f}V is below safe limit ({self.cutoff_voltage:.2f}V).")
        if m.max_sag_rate_mv_s > 15.0:
            m.warnings.append(f"High voltage sag rate observed ({m.max_sag_rate_mv_s:.1f} mV/s).")
        if m.c_rate_max > 2.0:
            m.warnings.append(f"Peak discharge C-rate exceeded 2.0C ({m.c_rate_max:.2f}C).")

        # Grade assignment
        if m.soh_pct >= 90.0 and m.rdc_median_mohm < 350.0:
            m.cell_grade = "Grade A (Prime)"
            m.cell_status_summary = "Optimal cell health, low internal impedance, and excellent energy delivery."
        elif m.soh_pct >= 75.0 or m.rdc_median_mohm < 500.0:
            m.cell_grade = "Grade B (Good)"
            m.cell_status_summary = "Healthy operational cell with moderate impedance rise; suitable for normal duty."
        else:
            m.cell_grade = "Grade C (Degraded)"
            m.cell_status_summary = "Significant capacity fade or elevated resistance; recommend cycling or retirement."


def load_and_analyze(file_path: str, nominal_capacity_ah: float = 2.0, cutoff_voltage: float = 3.2) -> BatteryDataset:
    """Loads a CSV file and runs full analysis."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    df = pd.read_csv(file_path)
    base_name = os.path.basename(file_path)
    return BatteryDataset(df, source_name=base_name, nominal_capacity_ah=nominal_capacity_ah, cutoff_voltage=cutoff_voltage)


def export_html_report(battery: BatteryDataset, output_path: str) -> str:
    """Generates an executive, dark-themed interactive HTML report with Chart.js visualization."""
    m = battery.metrics
    df = battery.df

    # Sample data points for web chart (max 80 points for lightweight web rendering)
    step = max(1, len(df) // 80)
    sampled = df.iloc[::step].copy()
    if sampled.iloc[-1]["Time"] != df.iloc[-1]["Time"]:
        sampled = pd.concat([sampled, df.iloc[[-1]]])

    time_labels = [f"{t:.0f}s" for t in sampled["Time"]]
    v_series = [round(float(x), 3) for x in sampled["Voltage"]]
    i_series = [round(float(x), 3) for x in sampled["Current"]]
    p_series = [round(float(x), 3) for x in sampled["Power"]]
    cap_series = [round(float(x) * 1000, 1) for x in sampled["Capacity_Ah"]]
    soc_series = [round(float(x), 1) for x in sampled["SoC_pct"]]

    # Grade badge color
    grade_color = "#10b981" if "Grade A" in m.cell_grade else ("#f59e0b" if "Grade B" in m.cell_grade else "#ef4444")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voltix Pro Battery Report - {battery.source_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-main: #0b0f17;
            --bg-card: #161f30;
            --bg-card-hover: #1e2a42;
            --border-color: #2a364f;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --cyan: #00e5ff;
            --emerald: #10b981;
            --amber: #f59e0b;
            --rose: #ef4444;
            --purple: #a855f7;
            --orange: #f97316;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: var(--bg-main); color: var(--text-main); padding: 30px 20px; line-height: 1.5; }}
        .container {{ max-width: 1280px; margin: 0 auto; }}
        
        /* Header */
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 20px; margin-bottom: 25px; flex-wrap: wrap; gap: 15px; }}
        .header-title {{ display: flex; align-items: center; gap: 12px; }}
        .badge {{ background: rgba(0, 229, 255, 0.15); color: var(--cyan); border: 1px solid var(--cyan); padding: 4px 10px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; text-transform: uppercase; }}
        .grade-badge {{ background: {grade_color}22; color: {grade_color}; border: 1px solid {grade_color}; padding: 6px 14px; border-radius: 20px; font-weight: 700; }}
        
        /* Grid KPIs */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 30px; }}
        .kpi-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 18px; position: relative; overflow: hidden; }}
        .kpi-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--cyan), var(--purple)); }}
        .kpi-label {{ font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
        .kpi-value {{ font-size: 1.8rem; font-weight: 700; color: var(--text-main); margin-bottom: 4px; }}
        .kpi-sub {{ font-size: 0.85rem; color: var(--text-muted); }}

        /* Chart Section */
        .chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(550px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .chart-box {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; }}
        .chart-box h3 {{ font-size: 1.1rem; color: var(--text-main); margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; }}

        /* Table */
        .details-box {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 22px; margin-bottom: 30px; }}
        .table-responsive {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; }}
        th, td {{ padding: 12px 14px; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }}
        th {{ color: var(--text-muted); font-weight: 600; background: rgba(0,0,0,0.2); }}
        tr:hover td {{ background: rgba(255,255,255,0.02); }}

        /* Warnings */
        .alert-box {{ background: rgba(239, 68, 68, 0.12); border: 1px solid var(--rose); border-radius: 8px; padding: 14px 18px; margin-bottom: 25px; }}
        .alert-box h4 {{ color: var(--rose); font-size: 0.95rem; margin-bottom: 5px; }}

        /* Footer */
        .footer {{ text-align: center; color: var(--text-muted); font-size: 0.85rem; border-top: 1px solid var(--border-color); padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div>
                <div class="header-title">
                    <h1 style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(90deg, #00e5ff, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ VOLTIX PRO ANALYZER</h1>
                    <span class="badge">Battery Test Report</span>
                </div>
                <p style="color: var(--text-muted); margin-top: 4px;">Source: <strong>{battery.source_name}</strong> | Test Duration: <strong>{m.duration_s:.0f}s ({m.duration_min:.1f} min)</strong> | Points: <strong>{m.data_points}</strong></p>
            </div>
            <div>
                <span class="grade-badge">{m.cell_grade}</span>
            </div>
        </div>

        {f'''<div class="alert-box">
            <h4>⚠️ Diagnostic Alerts</h4>
            <ul>{''.join([f"<li>{w}</li>" for w in m.warnings])}</ul>
        </div>''' if m.warnings else ''}

        <!-- Top Metrics Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Voltage Range</div>
                <div class="kpi-value">{m.v_initial:.2f}V &rarr; {m.v_final:.2f}V</div>
                <div class="kpi-sub">Total Drop: &Delta;{m.v_drop:.2f}V | Cutoff: {m.v_cutoff:.2f}V</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Delivered Capacity</div>
                <div class="kpi-value" style="color: var(--cyan);">{m.capacity_ah:.4f} Ah</div>
                <div class="kpi-sub">{m.capacity_mah:.1f} mAh ({m.soh_pct:.1f}% of {m.nominal_capacity_ah:.1f}Ah rating)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Delivered Energy</div>
                <div class="kpi-value" style="color: var(--emerald);">{m.energy_wh:.4f} Wh</div>
                <div class="kpi-sub">{m.energy_mwh:.1f} mWh | Avg V: {m.v_avg_discharge:.3f}V</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Current & Power</div>
                <div class="kpi-value">{m.i_mean:.2f}A / {m.p_mean:.2f}W</div>
                <div class="kpi-sub">Peak: {m.i_max:.2f}A ({m.c_rate_max:.2f}C) | Peak P: {m.p_max:.2f}W</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Internal Resistance</div>
                <div class="kpi-value" style="color: var(--amber);">{m.rdc_median_mohm:.0f} m&Omega;</div>
                <div class="kpi-sub">Final Sag: {m.rdc_final_mohm:.0f} m&Omega; | Plateau: {m.plateau_duration_s:.0f}s</div>
            </div>
        </div>

        <!-- Charts -->
        <div class="chart-grid">
            <div class="chart-box">
                <h3><span>Voltage Discharge Curve</span> <small style="color: var(--cyan); font-weight: normal;">V vs Time</small></h3>
                <canvas id="voltageChart" height="230"></canvas>
            </div>
            <div class="chart-box">
                <h3><span>Current & Power</span> <small style="color: var(--orange); font-weight: normal;">Dynamic Load</small></h3>
                <canvas id="currentPowerChart" height="230"></canvas>
            </div>
            <div class="chart-box">
                <h3><span>Delivered Capacity Accumulation</span> <small style="color: var(--emerald); font-weight: normal;">mAh vs Time</small></h3>
                <canvas id="capacityChart" height="230"></canvas>
            </div>
            <div class="chart-box">
                <h3><span>State of Charge Profile</span> <small style="color: var(--purple); font-weight: normal;">SoC% vs Time</small></h3>
                <canvas id="socChart" height="230"></canvas>
            </div>
        </div>

        <!-- Table Summary -->
        <div class="details-box">
            <h3 style="margin-bottom: 16px;">Comprehensive Battery Telemetry Summary</h3>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Value</th>
                            <th>Unit</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Initial Terminal Voltage</td><td><strong>{m.v_initial:.3f}</strong></td><td>V</td><td>Full resting state</td></tr>
                        <tr><td>Cutoff Terminal Voltage</td><td><strong>{m.v_final:.3f}</strong></td><td>V</td><td>End of discharge test</td></tr>
                        <tr><td>Thermodynamic Mean Voltage</td><td><strong>{m.v_avg_discharge:.3f}</strong></td><td>V</td><td>Calculated from Energy / Capacity integration</td></tr>
                        <tr><td>Total Voltage Sag (&Delta;V)</td><td><strong>{m.v_drop:.3f}</strong></td><td>V</td><td>Overall potential drop across discharge</td></tr>
                        <tr><td>Discharge Capacity (Trapezoidal)</td><td><strong>{m.capacity_ah:.4f}</strong></td><td>Ah</td><td>High-precision cumulative integration</td></tr>
                        <tr><td>Delivered Energy (Trapezoidal)</td><td><strong>{m.energy_wh:.4f}</strong></td><td>Wh</td><td>Cumulative instantaneous V &times; I integration</td></tr>
                        <tr><td>Average Current Draw</td><td><strong>{m.i_mean:.3f}</strong></td><td>A</td><td>Continuous discharge load</td></tr>
                        <tr><td>Maximum Current Peak</td><td><strong>{m.i_max:.3f}</strong></td><td>A</td><td>Peak transient drain</td></tr>
                        <tr><td>Average Power Dissipation</td><td><strong>{m.p_mean:.3f}</strong></td><td>W</td><td>Delivered battery power output</td></tr>
                        <tr><td>Peak Power Output</td><td><strong>{m.p_max:.3f}</strong></td><td>W</td><td>Max electrical power achieved</td></tr>
                        <tr><td>Estimated DC Internal Resistance</td><td><strong>{m.rdc_median_mohm:.1f}</strong></td><td>m&Omega;</td><td>Median &Delta;V/&Delta;I during dynamic transitions</td></tr>
                        <tr><td>Nominal Plateau Mean Voltage</td><td><strong>{m.plateau_v_mean:.3f}</strong></td><td>V</td><td>Stable voltage plateau duration: {m.plateau_duration_s:.0f}s</td></tr>
                        <tr><td>Knee Inflection Point</td><td><strong>{m.knee_voltage:.2f}V @ {m.knee_time_s:.0f}s</strong></td><td>-</td><td>Rapid depletion threshold onset</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            Generated automatically by <strong>Voltix Pro Battery Analyzer</strong> &bull; Advanced Electrochemical Test Report
        </div>
    </div>

    <script>
        const labels = {json.dumps(time_labels)};
        const vData = {json.dumps(v_series)};
        const iData = {json.dumps(i_series)};
        const pData = {json.dumps(p_series)};
        const capData = {json.dumps(cap_series)};
        const socData = {json.dumps(soc_series)};

        const chartOptions = {{
            responsive: true,
            plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
            scales: {{
                x: {{ grid: {{ color: '#1e293b' }}, ticks: {{ color: '#94a3b8' }} }},
                y: {{ grid: {{ color: '#1e293b' }}, ticks: {{ color: '#94a3b8' }} }}
            }}
        }};

        // Voltage Chart
        new Chart(document.getElementById('voltageChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Voltage (V)',
                    data: vData,
                    borderColor: '#00e5ff',
                    backgroundColor: 'rgba(0, 229, 255, 0.1)',
                    fill: true,
                    tension: 0.2,
                    borderWidth: 2,
                    pointRadius: 1
                }}]
            }},
            options: chartOptions
        }});

        // Current & Power Chart
        new Chart(document.getElementById('currentPowerChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: 'Current (A)',
                        data: iData,
                        borderColor: '#fb923c',
                        borderWidth: 2,
                        yAxisID: 'y',
                        pointRadius: 1
                    }},
                    {{
                        label: 'Power (W)',
                        data: pData,
                        borderColor: '#c084fc',
                        borderWidth: 2,
                        yAxisID: 'y1',
                        pointRadius: 1
                    }}
                ]
            }},
            options: {{
                ...chartOptions,
                scales: {{
                    ...chartOptions.scales,
                    y1: {{
                        position: 'right',
                        grid: {{ drawOnChartArea: false }},
                        ticks: {{ color: '#c084fc' }}
                    }}
                }}
            }}
        }});

        // Capacity Chart
        new Chart(document.getElementById('capacityChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Capacity (mAh)',
                    data: capData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.2,
                    borderWidth: 2,
                    pointRadius: 1
                }}]
            }},
            options: chartOptions
        }});

        // SoC Chart
        new Chart(document.getElementById('socChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'State of Charge (%)',
                    data: socData,
                    borderColor: '#818cf8',
                    backgroundColor: 'rgba(129, 140, 248, 0.1)',
                    fill: true,
                    tension: 0.2,
                    borderWidth: 2,
                    pointRadius: 1
                }}]
            }},
            options: chartOptions
        }});
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_path
