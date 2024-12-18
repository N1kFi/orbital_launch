import krpc
import math
import time
import json

# Конфигурация высот для гравитационного поворота и целевая орбита
turn_start_altitude = 250 # Высота начала гравитационного поворота
turn_end_altitude = 45_000 # Высота завершения гравитационного поворота
target_altitude = 150_000 # Целевая высота апогеи орбиты

# Подключение к серверу kRPC
conn = krpc.connect(name="Orbital Launch")
vessel = conn.space_center.active_vessel

# Настройка потоков данных для телеметрии
ut = conn.add_stream(getattr, conn.space_center, 'ut') # Поток времени (Universal Time)
m_all = vessel.mass # Масса ракеты
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude') # Поток текущей высоты над средним уровнем
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude') # Поток апогеи орбиты

# Настройка перед запуском
vessel.control.sas = False # Отключаем автоматическую стабилизацию (SAS)
vessel.control.rcs = False # Отключаем реактивное управление (RCS)
vessel.control.throttle = 1.0 # Устанавливаем тягу на 100%

# Обратный отсчет
print(3)
time.sleep(1)
print(2)
time.sleep(1)
print(1)
time.sleep(1)
print('Start!') # Печатаем сообщение о запуске с текущим временем

# Запуск ракеты
vessel.control.activate_next_stage() # Активируем первую ступень (запуск двигателей)
vessel.auto_pilot.engage() # Включаем автопилот
vessel.auto_pilot.target_pitch_and_heading(90, 90) # Задаем вертикальное направление (тангаж 90°, курс 90°)

# Переменные для отслеживания состояния
srbs_separated = 0  # Флаг для отсоединения ступеней
turn_angle = 0  # Текущий угол поворота ракеты
new_turn_angle = 0  # Новый рассчитанный угол поворота
time_values = []  # Массив для записи времени
speed_values = []  # Массив для записи скорости
altitude_values = []  # Массив для записи высоты
angle_values = []  # Массив для записи углов поворота

while True:
    # Получение текущих значений времени, скорости и высоты
    m = round(vessel.mass, 4)
    t = round(ut(), 4)
    v = round(vessel.flight(vessel.orbit.body.reference_frame).speed, 4)
    h = round(altitude(), 4)

    # Сохранение значений в массивы
    time_values.append(t)
    speed_values.append(v)
    altitude_values.append(h)
    mass_values.append(m)

    # Гравитационный поворот ракеты
    if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
        # Рассчитываем угол поворота на основе пропорции пройденного пути
        frac = (altitude() - turn_start_altitude) / (
                    turn_end_altitude - turn_start_altitude)
        new_turn_angle = 90 * frac # Угол поворота (максимум 90°)
        angle_values.append(new_turn_angle)
        
        # Если угол изменился достаточно, обновляем направление
        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)
    # Отсоединение ступеней, когда топливо заканчивается
    if srbs_separated != 2:
        resources = vessel.resources_in_decouple_stage(vessel.control.current_stage - 1, False) # Доступные ресурсы в текущей ступени
        if srbs_separated == 0:
            solid_fuel = resources.amount("SolidFuel") # Остаток твердого топлива
            if solid_fuel < 0.1: # Если топливо заканчивается
                # Отсоединяем ступень
                vessel.control.activate_next_stage()
                vessel.control.activate_next_stage()
                srbs_separated += 1
                print('Ступень - 1 отсоединена')
        elif srbs_separated == 1:
            liquid_fuel = resources.amount("LiquidFuel") # Остаток жидкого топлива
            if liquid_fuel < 0.1: # Если топливо заканчивается
                # Отсоединяем ступень
                vessel.control.activate_next_stage()
                vessel.control.activate_next_stage()
                srbs_separated += 1
                print('Ступень - 2 отсоединена')
    # Снижение тяги при приближении к целевой апогее
    if apoapsis() > target_altitude * 0.9:
        print('Приближаемся к апогее')
        break

vessel.control.throttle = 0.25 # Уменьшаем тягу для тонкой настройки

# Отключение двигателя при достижении целевой апогеи
while apoapsis() < target_altitude:
    t = round(conn.space_center.ut, 4)
    v = round(vessel.flight(vessel.orbit.body.reference_frame).speed, 4)
    h = round(altitude(), 4)
    m = round(vessel.mass, 4)

    time_values.append(t)
    speed_values.append(v)
    altitude_values.append(h)
    mass_values.append(m)
    pass

print('Апогея достигнута')
vessel.control.throttle = 0.0 # Полностью отключаем тягу

print('Выход за пределы атмосферы')
while altitude() < 70_500:
    t = round(conn.space_center.ut, 4)
    v = round(vessel.flight(vessel.orbit.body.reference_frame).speed, 4)
    h = round(altitude(), 4)
    m = round(vessel.mass, 4)

    time_values.append(t)
    speed_values.append(v)
    altitude_values.append(h)
    mass_values.append(m)
    pass


time_values = sorted(set(time_values))
speed_values = sorted(set(speed_values))
altitude_values = sorted(set(altitude_values))
angle_values = sorted(set(angle_values))
mass_values = sorted(set(mass_values))

# Логирование данных в файлы JSON
with open('speed_in_ksp.json', 'w') as f:
    json.dump(speed_values, f)
with open('time_in_ksp.json', 'w') as f:
    json.dump(time_values, f)
with open('altitude_in_ksp.json', 'w') as f:
    json.dump(altitude_values, f)
with open('angle_in_ksp.json', 'w') as f:
    json.dump(angle_values, f)
with open('mass_in_ksp.json', 'w') as f:
    json.dump(mass_values, f)

# Вычисление прироста скорости (дельта-v) для выхода на круговую орбиту
print('Вычисление приращения скорости для выхода на круговую орбиту')
mu = vessel.orbit.body.gravitational_parameter # Гравитационный параметр центрального тела
r = vessel.orbit.apoapsis # Радиус орбиты в апогее (расстояние от центра тела до ракеты)
a = vessel.orbit.semi_major_axis # Большая полуось орбиты
v1 = math.sqrt(mu * (2 / r - 1 / a)) # Текущая орбитальная скорость в апогее
v2 = math.sqrt(mu * (2 / r - 1 / r)) # Желаемая круговая скорость в апогее
dv = v2 - v1 # Прирост скорости для перехода на круговую орбиту
# Создание узла маневра
node = vessel.control.add_node(
    ut() + vessel.orbit.time_to_apoapsis, # Время выполнения маневра – момент достижения апогеи
    prograde=dv # Направление ускорения – вдоль орбиты
)
# Расчет времени горения двигателей (уравнение Циолковского)
F = vessel.available_thrust # Максимальная тяга двигателей
Im = vessel.specific_impulse * 9.82 # Удельный импульс двигателя (в м/с)
m0 = vessel.mass # Начальная масса ракеты (включая топливо)
m1 = m0 / math.exp(dv / Im) # Масса ракеты после маневра
flow_rate = F / Im # Расход топлива (масса/сек)
burn_time = (m0 - m1) / flow_rate # Время работы двигателя для выполнения маневра

# Ориентация ракеты для выполнения маневра
print('Ориентация корабля для округления орбиты')
vessel.auto_pilot.reference_frame = node.reference_frame # Установка системы координат узла маневра
vessel.auto_pilot.target_direction = (0, 1, 0) # Направление автопилота – по оси Y (вдоль орбиты)
vessel.auto_pilot.wait() # Ожидание стабилизации направления

# Перемотка времени к моменту начала маневра
print('Ждем пока округлит орбиту')
burn_ut = ut() + vessel.orbit.time_to_apoapsis - burn_time / 2 # Момент времени, чтобы начать маневр
lead_time = 5 # Время для завершения перемотки за несколько секунд до начала маневра
conn.space_center.warp_to(burn_ut - lead_time) # Перемотка времени

# Выполнение маневра
print('Готов к манёвру')
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis') # Поток времени до апогеи
while time_to_apoapsis() - (burn_time / 2) > 0: # Ожидание до момента начала маневра
    pass

# Включение двигателей для выполнения маневра
print('Осуществление манёвра')
vessel.control.throttle = 1.0 # Устанавливаем максимальную тягу
time.sleep(burn_time - 0.1) # Даем двигателям работать большую часть времени маневра

# Тонкая настройка
print('Тонкая настройка')
vessel.control.throttle = 0.05 # Снижаем тягу для более точной коррекции
remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame) # Оставшийся вектор маневра
while remaining_burn()[1] > 0 and ut() < 450: # Ожидаем завершения маневра
    pass
# Завершение маневра    
vessel.control.throttle = 0.0 # Останавливаем двигатели
node.remove() # Удаляем узел маневра
print('Запуск завершён. Ракета на орбите!')
