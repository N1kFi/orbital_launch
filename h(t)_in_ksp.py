import json
import numpy as np
import matplotlib.pyplot as plt

with open('altitude_in_ksp.json', 'r') as f:
    altitude_in_ksp = json.load(f)
with open('time_in_ksp.json', 'r') as f:
    time_in_ksp = json.load(f)

min_length = min(len(altitude_in_ksp), len(time_in_ksp))
time_in_ksp = time_in_ksp[:min_length]
altitude_in_ksp = altitude_in_ksp[:min_length]

x = np.array(time_in_ksp)
y = np.array(altitude_in_ksp)

plt.title('График высоты полёта ракеты от времени в KSP', fontsize=12, fontweight="bold")
plt.ylabel("Высота h(t)", fontsize=14)
plt.xlabel("Время t", fontsize=14)
plt.grid(True)
plt.plot(x - time_in_ksp[0], y, '-r', label='h(t)')
plt.show()