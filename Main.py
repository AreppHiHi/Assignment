import streamlit as st
import csv
import random
import pandas as pd

# ===================== REMOVE STREAMLIT DEFAULT HEADER/FOOTER =====================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ===================== PAGE TITLE =====================
st.title("Genetic Algorithm TV Scheduler")

# ===================== STEP 1: READ CSV =====================
def read_csv_to_dict(file_path):
    program_ratings = {}
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                program = row[0]
                ratings = [float(x) if x else 0.0 for x in row[1:]]
                program_ratings[program] = ratings
    except FileNotFoundError:
        st.error("File 'program_ratings_modified.csv' not found. Please ensure it’s in the same directory.")
    return program_ratings


# GA Functions =================================================
def fitness_function(schedule, ratings):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        if program in ratings and time_slot < len(ratings[program]):
            total_rating += ratings[program][time_slot]
    return total_rating

def initialize_population(all_programs, pop_size, schedule_length):
    population = []
    for _ in range(pop_size):
        schedule = [random.choice(all_programs) for _ in range(schedule_length)]
        population.append(schedule)
    return population

def crossover(schedule1, schedule2):
    point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:point] + schedule2[point:]
    child2 = schedule2[:point] + schedule1[point:]
    return child1, child2

def mutate(schedule, all_programs):
    idx = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[idx] = new_program
    return schedule

def genetic_algorithm(ratings, all_programs, generations, pop_size, crossover_rate, mutation_rate, elitism, schedule_length):
    population = initialize_population(all_programs, pop_size, schedule_length)
    for generation in range(generations):
        population.sort(key=lambda s: fitness_function(s, ratings), reverse=True)
        new_pop = population[:elitism]

        while len(new_pop) < pop_size:
            parent1, parent2 = random.choices(population, k=2)

            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                mutate(child1, all_programs)
            if random.random() < mutation_rate:
                mutate(child2, all_programs)

            new_pop.extend([child1, child2])

        population = new_pop[:pop_size]

    best = max(population, key=lambda s: fitness_function(s, ratings))
    return best


# ===================== STREAMLIT UI =====================
st.sidebar.header("GA Parameters")

file_path = "program_ratings_modified.csv"
ratings = read_csv_to_dict(file_path)

if ratings:
    all_programs = list(ratings.keys())

    # 6am to 23pm (18 hours)
    all_time_slots = list(range(6, 24))
    schedule_length = len(all_time_slots)

    st.sidebar.subheader("Trials Parameter")
    CO = st.sidebar.slider("Crossover Rate", 0.0, 1.0, 0.8, step=0.05)
    MUT = st.sidebar.slider("Mutation Rate", 0.0, 1.0, 0.2, step=0.01)

    GEN = 100
    POP = 100
    EL_S = 2

    st.write("### Sample Data from CSV")
    sample_df = pd.DataFrame(list(ratings.items()), columns=["Program", "Ratings"]).head(5)
    st.dataframe(sample_df)

    if st.button("Run GA"):
        best_schedule = genetic_algorithm(ratings, all_programs, GEN, POP, CO, MUT, EL_S, schedule_length)
        total_fitness = fitness_function(best_schedule, ratings)

        st.subheader("Final Schedule Result")
        st.metric("Total Fitness", round(total_fitness, 2))

        schedule_data = []
        for i, program in enumerate(best_schedule):
