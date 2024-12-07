import json
import matplotlib.pyplot as plt

# Загрузка данных
with open('mass_in_ksp.json') as f:
    mass_in_ksp = json.load(f)

with open('mass_math_model.json') as f:
    mass_math_model = json.load(f)

with open('time_in_ksp.json') as f:
    time = json.load(f)

# Вычисление времени относительно начала
time = [time[i] - time[0] for i in range(len(time))]

# Уравнивание длин массивов
min_length = min(len(mass_in_ksp), len(mass_math_model), len(time))
mass_in_ksp = list(reversed(mass_in_ksp[:min_length]))
mass_math_model = mass_math_model[:min_length]
time = time[:min_length]

# Построение графика
plt.figure(figsize=(10, 6))
plt.title('График массы ракеты от времени. Сравнение', fontsize=14, fontweight="bold")
plt.ylabel("Масса m(t), кг", fontsize=12)
plt.xlabel("Время t, сек", fontsize=12)
plt.grid(True)

# Графики
plt.plot(time, mass_in_ksp, '-r', label='Масса KSP')
plt.plot(time, mass_math_model, '-b', label='Масса по модели')

# Легенда и отображение
plt.legend(fontsize=12)
plt.show()
