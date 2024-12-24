import json
import matplotlib.pyplot as plt

with open('altitude_in_ksp.json', 'r') as f:
    altitude_in_ksp = json.load(f)
with open('distances_in_ksp.json', 'r') as f:
    distances_in_ksp = json.load(f)

min_length = min(len(altitude_in_ksp), len(distances_in_ksp))
altitude_in_ksp = altitude_in_ksp[:min_length]
distances_in_ksp = distances_in_ksp[:min_length]

plt.title('График траектории ракеты в KSP', fontsize=12, fontweight="bold")
plt.ylabel("Высота (м)", fontsize=14)
plt.xlabel("Расстояние (м)", fontsize=14)
plt.grid(True)
plt.plot(distances_in_ksp, altitude_in_ksp, label='Высота от расстояния ksp', color="red")
plt.show()