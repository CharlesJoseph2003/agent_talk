
import rover1


problems = {
    1: "Low Temp",
    2: "Bumpy surface detected",
    4: "Unidentified object ahead",
}

observations = {

}

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
        print("Rover2: Unknown problem, cannot proceed.")
        return None

def log_observation(key, description):
    observations[key] = description
    with open(SHARED_OBSERVATION_FILE, "a") as f:
        f.write(f"Rover2 - Observation {key}: {description}\n")

if __name__ == "__main__":
  
    detect_and_handle_problem(2)
    detect_and_handle_problem(4)
    detect_and_handle_problem(1)
    detect_and_handle_problem(3) 


    log_observation(202, "High rock concentration near coordinates (15.2, -23.7)")