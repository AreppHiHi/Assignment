import streamlit as st
import csv
import random
import pandas as pd

# REMOVE STREAMLIT DEFAULT HEADER/FOOTER
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("Genetic Algorithm TV Scheduler")

# READ CSV FILE
def read_csv_to_dict(file_path):
    program_ratings = {}
    try:
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                program = row[0]
                ratings = [float(x) if x else 0.0 for x in row[1:]]
                program_ratings[program] = ratings
    except FileNotFoundError:
        st.error("CSV not found")
    return program_ratings


# GA FUNCTIONS
def fitness_function(schedule, ratings):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

def initialize_population(programs, pop_size):
    return [random.sample(programs, len(programs)) for _ in range(pop_size)]

def crossover(schedule1, schedule2):
    point = random.randint(1, len(schedule1)-2)
    return schedule1[:point] + schedule2[point:], schedule2[:point] + schedule1[point:]

def mutate(schedule, programs):
    idx = random.randint(0, len(schedule)-1)
    schedule[idx] = random.choice(programs)
    return schedule

def run_ga(ratings, programs, gen, pop, co, mu, elitism):
    population = initialize_population(programs, pop)

    for g in range(gen):
        population.sort(key=lambda s: fitness_function(s, ratings), reverse=True)
        new_pop = population[:elitism]

        while len(new_pop) < pop:
            p1, p2 = random.choices(population, k=2)
            c1, c2 = crossover(p1, p2) if random.random() < co else (p1.copy(), p2.copy())

            if random.random() < mu: mutate(c1, programs)
            if random.random() < mu: mutate(c2, programs)
            new_pop += [c1, c2]

        population = new_pop[:pop]

    return population[0]


# UI SECTION
ratings = read_csv_to_dict("program_ratings_modified.csv")

if ratings:

    programs = list(ratings.keys())
    time_slots = list(range(6,24)) # 18 slot (6 - 23)

    GEN=100; POP=100; ELIT=2

    st.sidebar.header("Trial GA Parameters")

    CO1 = st.sidebar.slider("Trial 1 Crossover",0.0,1.0,0.8)
    MU1 = st.sidebar.slider("Trial 1 Mutation",0.0,1.0,0.2)

    CO2 = st.sidebar.slider("Trial 2 Crossover",0.0,1.0,0.8)
    MU2 = st.sidebar.slider("Trial 2 Mutation",0.0,1.0,0.2)

    CO3 = st.sidebar.slider("Trial 3 Crossover",0.0,1.0,0.8)
    MU3 = st.sidebar.slider("Trial 3 Mutation",0.0,1.0,0.2)

    if st.button("RUN 3 TRIAL"):
        trials = [("Trial 1",CO1,MU1),("Trial 2",CO2,MU2),("Trial 3",CO3,MU3)]

        for label,co,mu in trials:

            schedule = run_ga(ratings, programs, GEN, POP, co, mu, ELIT)

            schedule18 = schedule[:18]     # force output 18 slot only

            rows=[]
            for i,program in enumerate(schedule18):
                rows.append({
                    "Time Slot": f"{time_slots[i]:02d}:00",
                    "Program": program,
                    "Rating": round(ratings[program][i],1)   # 1 decimal
                })

            df = pd.DataFrame(rows)

            st.subheader(label)
            st.write(f"Crossover={co} , Mutation={mu}")
            st.dataframe(df)
