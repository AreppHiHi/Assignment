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

def run_ga(ratings, programs, gen, pop, co, mu, elitism_
