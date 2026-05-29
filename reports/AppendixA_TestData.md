# Приложение A — Тестовые данные

## A.1. Серийные номера изделий

| serial_number | product_type_name | status | id_shop | shop_name | id_category | category_name |
|---------------|-------------------|--------|---------|-----------|-------------|---------------|
| 1001 | Boeing 737-800 | ready | 1 | Shop 1 - Aircraft Assembly | 1 | Aircraft |
| 1002 | Boeing 737-800 | ready | 1 | Shop 1 - Aircraft Assembly | 1 | Aircraft |
| 1003 | Boeing 737-800 | ready | 1 | Shop 1 - Aircraft Assembly | 1 | Aircraft |
| 1004 | Airbus A320neo | in_assembly | 1 | Shop 1 - Aircraft Assembly | 1 | Aircraft |
| 1005 | Airbus A320neo | in_assembly | 1 | Shop 1 - Aircraft Assembly | 1 | Aircraft |
| 1006 | CFM56-7B Engine | under_test | 2 | Shop 2 - Engine Manufacturing | 2 | Engine |
| 1007 | CFM56-7B Engine | under_test | 2 | Shop 2 - Engine Manufacturing | 2 | Engine |
| 1008 | LEAP-1A Engine | in_assembly | 2 | Shop 2 - Engine Manufacturing | 2 | Engine |
| 1009 | Flight Control System | in_assembly | 3 | Shop 3 - Component Production | 3 | Avionics |
| 1010 | Flight Control System | in_assembly | 3 | Shop 3 - Component Production | 3 | Avionics |
| 1011 | Main Landing Gear | ready | 4 | Shop 4 - Final Assembly | 4 | Landing Gear |
| 1012 | Main Landing Gear | ready | 4 | Shop 4 - Final Assembly | 4 | Landing Gear |
| 1013 | Hydraulic Pump | in_assembly | 5 | Shop 5 - Testing Center | 5 | Components |
| 1014 | Fuel Control Unit | in_assembly | 5 | Shop 5 - Testing Center | 5 | Components |
| 1015 | Hydraulic Pump | under_test | 5 | Shop 5 - Testing Center | 5 | Components |

## A.2. Цеха (shops)

| id_shop | name |
|---------|------|
| 1 | Shop 1 - Aircraft Assembly |
| 2 | Shop 2 - Engine Manufacturing |
| 3 | Shop 3 - Component Production |
| 4 | Shop 4 - Final Assembly |
| 5 | Shop 5 - Testing Center |

## A.3. Участки (sections)

| id_section | name | id_shop | id_manager | manager_name |
|------------|------|---------|------------|--------------|
| 1 | Assembly Line 1 | 1 | 201 | Volkov Alexey Nikolaevich |
| 2 | Welding Shop | 1 | 202 | Lebedev Stanislav Ivanovich |
| 3 | Engine Test Stand | 2 | 203 | Orlov Nikolay Dmitrievich |
| 4 | Engine Assembly | 2 | 204 | Fedorov Pavel Alexeevich |
| 5 | Component Machining | 3 | 205 | Mikhailov Roman Sergeevich |
| 6 | Electronics Assembly | 3 | 206 | Vasiliev Igor Viktorovich |
| 7 | Final Inspection | 4 | 207 | Zaitsev Oleg Pavlovich |
| 8 | Quality Control | 5 | 201 | Volkov Alexey Nikolaevich |

## A.4. Бригады (brigades)

| id_brigade | name | id_section | id_foreman | foreman_name |
|------------|------|------------|------------|--------------|
| 1 | Brigade 1 - Assembly | 1 | 102 | Petrov Sergey Petrovich |
| 2 | Brigade 2 - Welding | 2 | 104 | Smirnov Dmitry Vladimirovich |
| 3 | Brigade 3 - Engine Test | 3 | 107 | Novikov Mikhail Andreevich |
| 4 | Brigade 4 - Machining | 5 | 107 | Novikov Mikhail Andreevich |
| 5 | Brigade 5 - Electronics | 6 | 107 | Novikov Mikhail Andreevich |

## A.5. Рабочие (workers)

| id_employee | last_name | first_name | profession | rank | is_foreman | id_brigade |
|-------------|-----------|------------|------------|------|------------|------------|
| 101 | Ivanov | Ivan | Fitter | 4 | false | 1 |
| 102 | Petrov | Sergey | Welder | 5 | true | 1 |
| 103 | Sidorov | Aleksandr | Fitter | 5 | false | 2 |
| 104 | Smirnov | Dmitry | CNC Operator | 4 | true | 2 |
| 105 | Kozlov | Andrey | Electrician | 6 | false | 3 |
| 106 | Morozov | Viktor | Welder | 4 | false | 3 |
| 107 | Novikov | Mikhail | Inspector | 5 | true | 4 |

## A.6. Инженеры (engineers)

| id_employee | last_name | first_name | category | position |
|-------------|-----------|------------|----------|----------|
| 201 | Volkov | Alexey | Engineer | Chief Engineer |
| 202 | Lebedev | Stanislav | Engineer | Senior Engineer |
| 203 | Orlov | Nikolay | Technologist | Chief Technologist |
| 204 | Fedorov | Pavel | Technologist | Technologist |
| 205 | Mikhailov | Roman | Engineer | Design Engineer |
| 206 | Vasiliev | Igor | Technician | Senior Technician |
| 207 | Zaitsev | Oleg | Master | Master |

## A.7. Испытатели (testers)

| id_employee | last_name | first_name | specialization | id_lab |
|-------------|-----------|------------|----------------|--------|
| 301 | Solovyov | Yuri | Engine Testing | 2 |
| 302 | Pavlov | Kirill | Vibration Testing | 4 |
| 303 | Sokolov | Maxim | Quality Control | 1 |
| 304 | Popov | Artur | Environmental Testing | 5 |
| 305 | Kuznetsov | Denis | Materials Testing | 3 |

## A.8. Лаборатории (laboratories)

| id_lab | type | name |
|--------|------|------|
| 1 | Quality Control | Lab 1 - Quality Control |
| 2 | Engine Test | Lab 2 - Engine Test Stand |
| 3 | Materials | Lab 3 - Materials Analysis |
| 4 | Vibration | Lab 4 - Vibration Testing |
| 5 | Environmental | Lab 5 - Environmental Test |

## A.9. Оборудование (equipment)

| id_equipment | name | model | id_lab |
|--------------|------|-------|--------|
| 1 | Vibration Tester | VT-2000 | 4 |
| 2 | Pressure Test Stand | PTS-500 | 2 |
| 3 | Spectral Analyzer | SA-1000 | 3 |
| 4 | Climate Chamber | CC-300 | 5 |
| 5 | CMM Machine | CMM-Hexagon | 1 |
| 6 | Ultrasonic Tester | UT-500 | 1 |
| 7 | Torque Tester | TT-200 | 2 |

## A.10. Категории изделий (product_categories)

| id_category | name |
|-------------|------|
| 1 | Aircraft |
| 2 | Engine |
| 3 | Avionics |
| 4 | Landing Gear |
| 5 | Components |

## A.11. Пользователи системы (users)

| login | password | role | id_employee |
|-------|----------|------|-------------|
| admin | admin123 | admin | NULL |
| hr_user | hr123 | hr_manager | NULL |
| master1 | master123 | master | 107 |
| brigadier1 | brig123 | foreman | 102 |
| tester1 | test123 | tester | 301 |
| technologist1 | tech123 | technologist | 201 |
| analyst1 | an1234 | analyst | NULL |

---

**Конец документа**
