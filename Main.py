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
    .block-container {padding-top: 20px;}
    </style>
""", unsafe_allow_html=True)

# ===================== PAGE TITLE =====================
st.title("Genetic Algorithm TV Scheduler")

# ===================== READ CSV FILE =====================
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
        st.error("Cannot find program_ratings_modified.csv")

    return program_ratings


# ===================== GA FUNCTIONS =====================
def fitness_function(schedule, ratings):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

def initialize_population(programs, pop_size):
    population = []
    for _ in range(pop_size):
        schedule = programs.copy()
        random.shuffle(schedule)
        population.append(schedule)
    return population

def crossover(schedule1, schedule2):
    point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:point] + schedule2[point:]
    child2 = schedule2[:point] + schedule1[point:]
    return child1, child2

def mutate(schedule, all_programs):
    idx = random.randint(0, len(schedule) - 1)
    schedule[idx] = random.choice(all_programs)
    return schedule

def genetic_algorithm(ratings, all_programs, generations, pop_size, crossover_rate, mutation_rate, elitism):
    population = initialize_population(all_programs, pop_size)

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

ratings = read_csv_to_dict("program_ratings_modified.csv")

if ratings:

    all_programs = list(ratings.keys())
    all_time_slots = list(range(6, 24))  # 6am to 23pm = 18 hours

    GEN = 100
    POP = 100
    EL_S = 2

    # TRIAL parameters
    st.sidebar.subheader("Trial 1")
    CO_R1 = st.sidebar.slider("Crossover", 0.0, 1.0, 0.8, step=0.05, key="co1")
    MUT_R1 = st.sidebar.slider("Mutation", 0.0, 1.0, 0.2, step=0.01, key="mu1")

    st.sidebar.subheader("Trial 2")
    CO_R2 = st.sidebar.slider("Crossover ", 0.0, 1.0, 0.8, step=0.05, key="co2")
    MUT_R2 = st.sidebar.slider("Mutation ", 0.0, 1.0, 0.2, step=0.01, key="mu2")

    st.sidebar.subheader("Trial 3")
    CO_R3 = st.sidebar.slider("Crossover  ", 0.0, 1.0, 0.8, step=0.05, key="co3")
    MUT_R3 = st.sidebar.slider("Mutation  ", 0.0, 1.0, 0.2, step=0.01, key="mu3")

    st.write("Sample 5 Program Data:")
    st.dataframe(pd.DataFrame(list(ratings.items()), columns=["Program", "Ratings"]).head(5))

    if st.button("Run All Trials"):
        trials = [
            ("Trial 1", CO_R1, MUT_R1),
            ("Trial 2", CO_R2, MUT_R2),
            ("Trial 3", CO_R3, MUT_R3),
        ]

        for name, co_rate, mut_rate in trials:
            best_schedule = genetic_algorithm(ratings, all_programs, GEN, POP, co_rate, mut_rate, EL_S)
            total_fit = fitness_function(best_schedule, ratings)

            st.subheader(name)
            st.write(f"Crossover: {co_rate} | Mutation: {mut_rate}")
            st.write(f"Total Fitness: {round(total_fit,2)}")

            schedule_data = []
            for i, program in enumerate(best_schedule):
                schedule_data.append({
                    "Time Slot": f"{all_time_slots[i]:02d}:00",
                    "Program": program,
                    "Rating": round(ratings[program][i], 2)
                })

            st.dataframe(pd.DataFrame(schedule_data))
            st.markdown("---")
