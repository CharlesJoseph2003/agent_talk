
import rover1

problems = {
    1: "Low Temp",
    2: "Bumpy surface detected",
    4: "Unidentified object ahead"
}

observations = {}
SHARED_OBSERVATION_FILE = "shared_observations.txt"

request_count = 0

def detect_and_handle_problem(problem_key):
    global request_count

    if request_count >= rover1.MAX_REQUESTS:
        print("Rover2: Exceeded maximum allowed solution requests.")
        return None

    if problem_key in problems:
        print(f"Rover2: Problem detected - {problems[problem_key]}")
        request_count += 1
        solution = rover1.get_solution(problem_key, request_count)
        print(f"Rover2: Retrieved solution from Rover1 - {solution}")
        return solution

    else:
        print(f"Rover2: Unknown problem key {problem_key}. Sending data to Rover1 for help.")
        rover_obs = observations.get(problem_key, "No local observation.")
        new_solution = rover1.handle_unknown_problem(problem_key, "Rover2", rover_obs)

       
        problems[problem_key] = new_solution
        print(f"Rover2: New solution for problem {problem_key} saved.")
        return new_solution

def log_observation(key, description):
    observations[key] = description
    with open(SHARED_OBSERVATION_FILE, "a") as f:
        f.write(f"Rover2 - Observation {key}: {description}\n")

if __name__ == "__main__":
    log_observation(4, "Metallic object reflecting sunlight")
    detect_and_handle_problem(4)  
    detect_and_handle_problem(5)  
