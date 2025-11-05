import streamlit as st
import csv
import random
import pandas as pd

# ================= STREAMLIT UI =================
st.title("TV Program Rating - Genetic Algorithm Optimizer")

# Sliders input user
CO_R = st.slider("Crossover Rate (CO_R)", 0.0, 0.95, 0.8)
MUT_R = st.slider("Mutation Rate (MUT_R)", 0.01, 0.05, 0.02)

# Load CSV
def read_csv_to_dict(file_path):
    program_ratings = {}
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]
            program_ratings[program] = ratings
    return program_ratings

file_path = 'program_ratings_modified.csv'
ratings = read_csv_to_dict(file_path)

GEN = 100
POP = 50
EL_S = 2
all_programs = list(ratings.keys())
all_time_slots = list(range(6,24)) # 6pm - 11pm = 18 slots

def fitness_function(schedule):
    return sum(ratings[program][i] for i, program in enumerate(schedule))

def initialize_pop(programs, time_slots):
    if not programs:
        return [[]]
    all_schedules=[]
    for i in range(len(programs)):
        for schedule in initialize_pop(programs[:i]+programs[i+1:], time_slots):
            all_schedules.append([programs[i]] + schedule)
    return all_schedules

def finding_best_schedule(all_schedules):
    return max(all_schedules, key=fitness_function)

all_possible_schedules = initialize_pop(all_programs, all_time_slots)
initial_best_schedule = finding_best_schedule(all_possible_schedules)

def crossover(schedule1,schedule2):
    cut = random.randint(1,len(schedule1)-2)
    return (schedule1[:cut]+schedule2[cut:], schedule2[:cut]+schedule1[cut:])

def mutate(schedule):
    schedule[random.randint(0,len(schedule)-1)] = random.choice(all_programs)
    return schedule

def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R):
    population=[initial_schedule]
    for _ in range(population_size-1):
        x=initial_schedule.copy()
        random.shuffle(x)
        population.append(x)
    for gen in range(generations):
        new_pop=[]
        population.sort(key=fitness_function, reverse=True)
        new_pop.extend(population[:EL_S])
        while len(new_pop)<population_size:
            p1,p2 = random.choices(population,k=2)
            if random.random()<crossover_rate:
                c1,c2=crossover(p1,p2)
            else:
                c1,c2=p1.copy(),p2.copy()
            if random.random()<mutation_rate: mutate(c1)
            if random.random()<mutation_rate: mutate(c2)
            new_pop.extend([c1,c2])
        population=new_pop
    return population[0]

if st.button("RUN GENETIC ALGORITHM"):

    genetic_schedule = genetic_algorithm(initial_best_schedule, crossover_rate=CO_R, mutation_rate=MUT_R)

    final_schedule = genetic_schedule[:len(all_time_slots)]

    while len(final_schedule) < len(all_time_slots):
        final_schedule.append(random.choice(all_programs))

    df = pd.DataFrame({
        "Time Slot": [f"{ts:02d}:00" for ts in all_time_slots],
        "Program": final_schedule
    })

    st.subheader("Final Optimal Schedule Table")
    st.table(df)

    st.write("Total Ratings:", fitness_function(final_schedule))
