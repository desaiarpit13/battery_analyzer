# 🔋 Battery Analyzer

A beginner-friendly Python project for analyzing battery performance using **voltage, current, power, capacity, and energy data**.

The project takes battery measurements from a CSV file, processes the data using Python, generates graphs, and produces an automatic battery analysis report.

---

## 📌 Project Overview

The **Battery Analyzer** is designed to turn raw battery measurement data into useful information.

Instead of manually analyzing every measurement, the Python program automatically calculates:

* 🔌 Initial Voltage
* 🔋 Final Voltage
* 📉 Voltage Drop
* ⚡ Average Current
* ⚡ Maximum Current
* 🔥 Average Power
* 🔥 Maximum Power
* 🔋 Delivered Capacity
* ⚡ Delivered Energy

It also generates graphs showing how the battery parameters change with time.

---

## 🛠️ Technologies Used

* **Python**
* **Pandas** — Data processing and analysis
* **NumPy** — Numerical operations
* **Matplotlib** — Data visualization
* **CSV** — Battery measurement data storage

---

## 📂 Project Structure

```text
Batery Analyzer/
│
├── Battery_analyzer.py
├── battery_data.csv
└── README.md
```

> Note: The project folder is named `Batery Analyzer` in the current version.

---

## 📊 Input Data

The program reads battery measurements from:

```text
battery_data.csv
```

The CSV file contains:

| Column  | Description      | Unit    |
| ------- | ---------------- | ------- |
| Time    | Measurement time | seconds |
| Voltage | Battery voltage  | V       |
| Current | Battery current  | A       |

### Example

```csv
Time,Voltage,Current
0,4.20,2.00
10,4.15,2.01
20,4.10,2.00
30,4.05,1.98
40,4.00,2.02
50,3.95,2.00
```

---

## ⚙️ How It Works

### 1. Read the CSV

The program loads the battery data using Pandas.

```python
data = pd.read_csv("battery_data.csv")
```

### 2. Calculate Power

Power is calculated using:

```text
Power = Voltage × Current
```

```python
data["Power"] = data["Voltage"] * data["Current"]
```

---

### 3. Calculate Time Difference

The program calculates the time difference between consecutive measurements:

```python
data["dt"] = data["Time"].diff().fillna(0)
```

---

### 4. Calculate Capacity

Battery capacity is estimated using:

```text
Capacity (Ah) = Current × Time / 3600
```

The program performs cumulative integration:

```python
data["Capacity_Ah"] = (
    data["Current"] * data["dt"]
).cumsum() / 3600
```

---

### 5. Calculate Energy

Energy is calculated from power over time:

```text
Energy (Wh) = Power × Time / 3600
```

```python
data["Energy_Wh"] = (
    data["Power"] * data["dt"]
).cumsum() / 3600
```

---

## 📈 Graphs Generated

The program generates five graphs:

### 1. Voltage vs Time

Shows how the battery voltage changes during the measurement.

### 2. Current vs Time

Shows the current drawn from the battery.

### 3. Power vs Time

Shows the instantaneous power calculated from voltage and current.

### 4. Capacity vs Time

Shows the accumulated charge delivered by the battery.

### 5. Energy vs Time

Shows the accumulated energy delivered by the battery.

---

## 📋 Automatic Battery Report

After processing the data, the program generates a report similar to:

```text
======================================
          BATTERY ANALYSIS
======================================

Initial Voltage      : 4.20 V
Final Voltage        : 3.20 V
Voltage Drop         : 1.00 V

Average Current      : 1.85 A
Maximum Current      : 2.05 A

Average Power        : 6.25 W
Maximum Power        : 8.61 W

Delivered Capacity   : 1.2345 Ah
Delivered Energy     : 4.5678 Wh

======================================
         ANALYSIS COMPLETE
======================================
```

---

## 🚀 How to Run

### Step 1 — Install Python

Make sure Python is installed on your computer.

Check using:

```bash
python --version
```

---

### Step 2 — Install Required Libraries

Run:

```bash
pip install pandas numpy matplotlib
```

---

### Step 3 — Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Then enter the project directory:

```bash
cd "Batery Analyzer"
```

---

### Step 4 — Add Battery Data

Make sure:

```text
battery_data.csv
```

is present in the same folder as:

```text
Battery_analyzer.py
```

---

### Step 5 — Run the Program

```bash
python Battery_analyzer.py
```

The program will generate the graphs and print the battery analysis report in the terminal.

---

## 🎯 Project Goals

This project was built to practice:

* Python programming
* Pandas data analysis
* NumPy numerical calculations
* Matplotlib visualization
* CSV data handling
* Basic battery analysis
* Engineering data interpretation

The larger goal is to understand how **real battery measurement data can be processed using programming**.

---

## 🔬 Current Limitations

This is a **basic battery data-analysis tool**, not a complete Battery Management System (BMS).

Currently, it does not directly perform:

* State of Charge (SOC) estimation
* State of Health (SOH) estimation
* Battery temperature analysis
* Cell balancing
* Cycle-life analysis
* Internal resistance estimation
* Coulombic efficiency calculation
* Battery degradation modeling

These are potential future improvements.

---

## 🔮 Future Improvements

Possible upgrades include:

### Level 1 — More Measurements

Add:

* Temperature
* Multiple battery cells
* Charging/discharging state

### Level 2 — Battery Health

Implement:

* SOC estimation
* SOH estimation
* Capacity degradation
* Cycle counting

### Level 3 — Advanced Analysis

Add:

* Internal resistance estimation
* Voltage sag analysis
* Charge/discharge curve analysis
* Battery efficiency
* Cycle-to-cycle comparison

### Level 4 — Visualization

Build an interactive dashboard using tools such as:

* Plotly
* Streamlit

### Level 5 — Real-Time Battery Analyzer

Connect the software to actual hardware sensors and allow Python to analyze battery measurements in real time.

---

## ⚠️ Important Note

The accuracy of the analysis depends on the quality and sampling interval of the input data.

The calculated capacity and energy are estimates based on the voltage, current, and time measurements provided in the CSV file.

This project is intended for **learning and engineering analysis**, not for safety-critical battery management.

---

## 👨‍💻 Author

**Arpit Desai**

Engineering Student | Electronics | Battery Technology | Python

---

## 📜 License

This project is open-source and available for educational and personal use.
