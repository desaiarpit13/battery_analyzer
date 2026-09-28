import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv("battery_data.csv")

data["Time"] = pd.to_numeric(data["Time"])
data["Voltage"] = pd.to_numeric(data["Voltage"])
data["Current"] = pd.to_numeric(data["Current"])

# Power
data["Power"] = data["Voltage"] * data["Current"]

# Time difference
data["dt"] = data["Time"].diff().fillna(0)

# Capacity
data["Capacity_Ah"] = (
    data["Current"] * data["dt"]
).cumsum() / 3600

# Energy
data["Energy_Wh"] = (
    data["Power"] * data["dt"]
).cumsum() / 3600


# ================= GRAPHS =================

fig, axes = plt.subplots(5, 1, figsize=(10, 14))

# 1. Voltage
axes[0].plot(data["Time"], data["Voltage"])
axes[0].set_title("Voltage vs Time")
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Voltage (V)")
axes[0].grid()

# 2. Current
axes[1].plot(data["Time"], data["Current"])
axes[1].set_title("Current vs Time")
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Current (A)")
axes[1].grid()

# 3. Power
axes[2].plot(data["Time"], data["Power"])
axes[2].set_title("Power vs Time")
axes[2].set_xlabel("Time (s)")
axes[2].set_ylabel("Power (W)")
axes[2].grid()

# 4. Capacity
axes[3].plot(data["Time"], data["Capacity_Ah"])
axes[3].set_title("Capacity vs Time")
axes[3].set_xlabel("Time (s)")
axes[3].set_ylabel("Capacity (Ah)")
axes[3].grid()

# 5. Energy
axes[4].plot(data["Time"], data["Energy_Wh"])
axes[4].set_title("Energy vs Time")
axes[4].set_xlabel("Time (s)")
axes[4].set_ylabel("Energy (Wh)")
axes[4].grid()

plt.tight_layout()
plt.show()


# ================= BATTERY REPORT =================

initial_voltage = data["Voltage"].iloc[0]
final_voltage = data["Voltage"].iloc[-1]
voltage_drop = initial_voltage - final_voltage

average_current = data["Current"].mean()
maximum_current = data["Current"].max()

average_power = data["Power"].mean()
maximum_power = data["Power"].max()

delivered_capacity = data["Capacity_Ah"].iloc[-1]
delivered_energy = data["Energy_Wh"].iloc[-1]


print("\n======================================")
print("          BATTERY ANALYSIS")
print("======================================")

print(f"\nInitial Voltage      : {initial_voltage:.2f} V")
print(f"Final Voltage        : {final_voltage:.2f} V")
print(f"Voltage Drop         : {voltage_drop:.2f} V")

print(f"\nAverage Current      : {average_current:.2f} A")
print(f"Maximum Current      : {maximum_current:.2f} A")

print(f"\nAverage Power        : {average_power:.2f} W")
print(f"Maximum Power        : {maximum_power:.2f} W")

print(f"\nDelivered Capacity   : {delivered_capacity:.4f} Ah")
print(f"Delivered Energy     : {delivered_energy:.4f} Wh")

print("\n======================================")
print("         ANALYSIS COMPLETE")
print("======================================")