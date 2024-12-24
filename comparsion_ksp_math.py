import json

import numpy as np
import matplotlib.pyplot as plt

# Константы для планеты Кербин
G = 6.67430e-11  # Гравитационная постоянная, м^3/(кг*с^2)
M_kerbin = 5.2915793e22  # Масса Кербина, кг
R_kerbin = 600000  # Радиус Кербина, м

g0 = G * M_kerbin / R_kerbin**2  # Ускорение свободного падения на поверхности Кербина, м/с^2

# Атмосферные параметры для Кербина
rho0 = 1.225  # Плотность воздуха на уровне моря, кг/м^3
H = 70000  # Скорректированная высота атмосферы, м
Cd = 0.5  # Коэффициент сопротивления
A = 5  # Площадь поперечного сечения ракеты, м^2 (увеличена для увеличения сопротивления)

# Параметры ракеты
stages = [
    # 1-я ступень: 4 турбоускорителя "Молот"
    {"wet_mass": 20000, "fuel_mass": 12000, "thrust": 900000, "burn_time": 41},  # Увеличена тяга
    # 2-я ступень: 3 топливных бака "FL-T400" и ЖРД "Аертлявый"
    {"wet_mass": 9500, "fuel_mass": 5000, "thrust": 450000, "burn_time": 88},  # Увеличена тяга
    # 3-я ступень: 1 топливный бак "FL-T400", ЖРД "Терьер", командный отсек "МК1"
    {"wet_mass": 3000, "fuel_mass": 1500, "thrust": 70000, "burn_time": 31}
]

# Временные параметры
dt = 0.01  # Шаг интегрирования, с
T_total = sum(stage["burn_time"] for stage in stages)  # Общее время моделирования, с
time = np.arange(0, T_total, dt)

# Ограничения
rho_min = 1e-6  # Минимальная плотность воздуха

# Уравнения движения ракеты
def rocket_dynamics(t, state, stage):
    x, y, vx, vy, m = state

    # Ограничение на минимальную высоту и массу
    if y < 0:
        y = 0
        vy = 0

    # Расчет текущих сил
    r = max(np.sqrt(x*2 + y*2), R_kerbin)  # Минимальная дистанция — радиус Кербина
    g_force = G * M_kerbin / r**2  # Сила тяжести
    rho = max(rho0 * np.exp(-y / H), rho_min)  # Плотность воздуха
    velocity = np.sqrt(vx*2 + vy*2)  # Общая скорость

    # Учитываем сопротивление воздуха
    if velocity > 1e-3:  # если скорость ракеты слишком мала, сопротивление не учитываем
        drag = 0.5 * Cd * rho * A * velocity**2  # Сопротивление воздуха
    else:
        drag = 0  # при очень низкой скорости сопротивление можно игнорировать

    # Вертикальная тяга и ускорение
    thrust_vertical = stage["thrust"]  # Тяга полностью вертикальная

    if velocity < 1e-3:
        ax = 0  # Если скорость слишком мала, не применяем ускорение
        ay = (thrust_vertical - g_force) / m  # Если ракета замедляется или стоит, убираем влияние сопротивления
    else:
        ay = (thrust_vertical - g_force - drag * vy / velocity) / m  # Ускорение по вертикали
        ax = 0  # Горизонтальная скорость не изменяется (моделируем вертикальный полет)

    # Производные
    dxdt = vx
    dydt = vy
    dvxdt = ax
    dvydt = ay

    # Линейное уменьшение массы
    fuel_rate = stage["fuel_mass"] / stage["burn_time"]
    dmdt = -fuel_rate

    return np.array([dxdt, dydt, dvxdt, dvydt, dmdt])

# Метод Рунге-Кутта 4-го порядка
def runge_kutta(f, t, state, stage):
    k1 = f(t, state, stage)
    k2 = f(t + dt / 2, state + dt * k1 / 2, stage)
    k3 = f(t + dt / 2, state + dt * k2 / 2, stage)
    k4 = f(t + dt, state + dt * k3, stage)
    return state + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6

# Начальные условия
state = np.array([0, 0, 0, 0, stages[0]["wet_mass"]])  # Начальные координаты, скорость и масса
trajectory = []  # Двумерный массив для хранения траекторий
mass = []  # Массив для хранения полной массы

# Решение системы
current_stage = 0
stage_time = 0
for t in time:
    if current_stage >= len(stages):
        break

    # Запись текущей массы и траектории
    trajectory.append(state.copy())
    mass.append(state[4])

    # Переход между этапами
    if stage_time >= stages[current_stage]["burn_time"]:
        stage_time = 0
        current_stage += 1
        if current_stage >= len(stages):
            break
        state[4] = stages[current_stage]["wet_mass"]  # Обновление массы

    if state[4] <= 0:  # Проверка массы
        break

    state = runge_kutta(rocket_dynamics, t, state, stages[current_stage])
    stage_time += dt

# Преобразуем траекторию в двумерный массив
trajectory = np.array(trajectory)
# Расчет зависимостей
altitude = trajectory[:, 1]
speed = np.sqrt(trajectory[:, 2]*2 + trajectory[:, 3]*2)*16  # Исправленная формула для скорости
vert_speed = trajectory[:, 3]
horz_speed = trajectory[:, 2]
distance = np.sqrt(trajectory[:, 0]*2 + trajectory[:, 1]*2)

# Построение графиков
plt.figure(figsize=(12, 7))

# 1. Высота от времени
plt.subplot(2, 1, 1)
plt.plot(time[:len(altitude)], altitude/10, label='Высота', color='blue')

with open('altitude_in_ksp.json', 'r') as f:
    altitude_in_ksp = json.load(f)
with open('time_in_ksp.json', 'r') as f:
    time_in_ksp = json.load(f)

min_length = min(len(altitude_in_ksp), len(time_in_ksp))
altitude_in_ksp = altitude_in_ksp[:min_length]
time_in_ksp = time_in_ksp[:min_length]

x = np.array(time_in_ksp)
y = np.array(altitude_in_ksp)
plt.plot(x - time_in_ksp[0], y, label='Высота ksp', color='red')

plt.title('Высота от времени')
plt.xlabel('Время (с)')
plt.ylabel('Высота (м)')
plt.legend()
plt.grid()

# 2. Скорость от времени
plt.subplot(2, 1, 2)
plt.plot(time[:len(speed)], speed, label='Скорость', color='blue')

with open('speed_in_ksp.json', 'r') as f:
    speed_in_ksp = json.load(f)
with open('time_in_ksp.json', 'r') as f:
    time_in_ksp = json.load(f)

min_length = min(len(speed_in_ksp), len(time_in_ksp))
speed_in_ksp = speed_in_ksp[:min_length]
time_in_ksp = time_in_ksp[:min_length]

x = np.array(time_in_ksp)
y = np.array(speed_in_ksp)

plt.plot(x - time_in_ksp[0], y, label='Скорость ksp', color='red')
plt.title('Скорость от времени')
plt.xlabel('Время (с)')
plt.ylabel('Скорость (м/с)')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()