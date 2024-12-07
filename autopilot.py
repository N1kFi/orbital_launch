import krpc
import math
import time
import json

turn_start_altitude = 250
turn_end_altitude = 45_000
target_altitude = 150_000

conn = krpc.connect(name="Orbital Launch")
vessel = conn.space_center.active_vessel
print(vessel.name)

ut = conn.add_stream(getattr, conn.space_center, 'ut')
m_all = vessel.mass
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0

print(3)
time.sleep(1)
print(2)
time.sleep(1)
print(1)
time.sleep(1)
print('Start!')

vessel.control.activate_next_stage()
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)

srbs_separated = 0
turn_angle = 0
new_turn_angle = 0
time_values = []
speed_values = []
altitude_values = []
angle_values = []
mass_values = []

while True:
    m = round(vessel.mass, 4)
    t = round(ut(), 4)
    v = round(vessel.flight(vessel.orbit.body.reference_frame).speed, 4)
    h = round(altitude(), 4)
    time_values.append(t)
    speed_values.append(v)
    altitude_values.append(h)
    mass_values.append(m)

    if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
        frac = (altitude() - turn_start_altitude) / (
                    turn_end_altitude - turn_start_altitude)
        new_turn_angle = 90 * frac
        angle_values.append(new_turn_angle)

        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)

    if srbs_separated != 2:
        resources = vessel.resources_in_decouple_stage(vessel.control.current_stage - 1, False)
        if srbs_separated == 0:
            solid_fuel = resources.amount("SolidFuel")  # ТТ
            if solid_fuel < 0.1:
                vessel.control.activate_next_stage()
                vessel.control.activate_next_stage()
                srbs_separated += 1
                print('Ступень - 1 отсоединена')
        elif srbs_separated == 1:
            liquid_fuel = resources.amount("LiquidFuel")  # ЖТ
            if liquid_fuel < 0.1:
                vessel.control.activate_next_stage()
                vessel.control.activate_next_stage()
                srbs_separated += 1
                print('Ступень - 2 отсоединена')

    if apoapsis() > target_altitude * 0.9:
        print('Приближаемся к апогее')
        break

vessel.control.throttle = 0.25

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
vessel.control.throttle = 0.0

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

print('Вычисление приращения скорости для выхода на круговую орбиту')
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a = vessel.orbit.semi_major_axis
v1 = math.sqrt(mu * (2 / r - 1 / a))
v2 = math.sqrt(mu * (2 / r - 1 / r))
dv = v2 - v1
node = vessel.control.add_node(ut() + vessel.orbit.time_to_apoapsis,
                               prograde=dv)

F = vessel.available_thrust
Im = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(dv / Im)
flow_rate = F / Im
burn_time = (m0 - m1) / flow_rate

print('Ориентация корабля для округления орбиты')
vessel.auto_pilot.reference_frame = node.reference_frame
vessel.auto_pilot.target_direction = (0, 1, 0)
vessel.auto_pilot.wait()

print('Ждем пока округлит орбиту')
burn_ut = ut() + vessel.orbit.time_to_apoapsis - burn_time / 2
lead_time = 5
conn.space_center.warp_to(burn_ut - lead_time)

print('Готов к манёвру')
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit,
                                   'time_to_apoapsis')
while time_to_apoapsis() - (burn_time / 2) > 0:
    pass

print('Осуществление манёвра')
vessel.control.throttle = 1.0
time.sleep(burn_time - 0.1)

print('Тонкая настройка')
vessel.control.throttle = 0.05
remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)
while remaining_burn()[1] > 0 and ut() < 450:
    pass
vessel.control.throttle = 0.0
node.remove()
print('Запуск завершён')