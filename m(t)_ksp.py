import json
import numpy as np
import matplotlib.pyplot as plt

with open('mass_in_ksp.json', 'r') as f:
    mass_in_ksp = json.load(f)

with open('time_in_ksp.json', 'r') as f:
    time_in_ksp = json.load(f)

min_length = min(len(mass_in_ksp), len(time_in_ksp))
mass_in_ksp = list(reversed(mass_in_ksp[:min_length]))
time_in_ksp = time_in_ksp[:min_length]

x = np.array(time_in_ksp)
y = np.array(mass_in_ksp)

plt.title('График массы ракеты от времени в KSP', fontsize=12, fontweight="bold")
plt.ylabel("Масса m(t)", fontsize=14)
plt.xlabel("Время t", fontsize=14)
plt.grid(True)
plt.plot(x - time_in_ksp[0], y, '-r', label='m(t)')
plt.show()