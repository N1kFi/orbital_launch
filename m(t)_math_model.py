import json
import matplotlib.pyplot as plt

def m(t):
    if t == 0:
        return 26995
    elif 0 < t <= 41:
        return 26995 - 2810 * 4 / 41 * t
    elif 41 < t <= 129:
        return 12625 - 2000 * 4 / 88 * (t - 41)
    elif 129 < t <= 155:
        return 3780 - 2000 / 352 * (t - 129)
    elif 155 < t <= 158:
        return 3632
    elif 158 < t <= 499:
        return 3780 - 2000 / 352 * (t - 158 + 26)

# Время в ksp
with open('time_in_ksp.json', 'r') as f:
    time_in_ksp = json.load(f)

mass_model_stat = []
for t in time_in_ksp:
    t = t - time_in_ksp[0]
    mass_model_stat.append(m(t))

#График

with open('mass_math_model.json', 'w') as f:
    json.dump(mass_model_stat, f)
with open('mass_in_ksp.json') as f:
    mass_in_ksp = json.load(f)
with open('mass_math_model.json') as f:
    mass_math_model = json.load(f)
with open('time_in_ksp.json') as f:
    time = json.load(f)

time = [time[i] - time[0] for i in range(len(time))]

min_length = min(len(mass_in_ksp), len(mass_math_model), len(time))
mass_in_ksp = list(reversed(mass_in_ksp[:min_length]))
mass_math_model = mass_math_model[:min_length]
time = time[:min_length]

plt.figure(figsize=(10, 6))
plt.title('График массы ракеты от времени по модели', fontsize=14, fontweight="bold")
plt.ylabel("Масса m(t), кг", fontsize=12)
plt.xlabel("Время t, сек", fontsize=12)
plt.grid(True)
plt.plot(time, mass_math_model, '-b', label='Масса по модели')
plt.legend(fontsize=12)
plt.show()

