
problems = {
    1: "Low temperature detected - Activate heaters",
    2: "Bumpy surface ahead - Go around the area",
    3: "Dust storm approaching - Seek shelter"
}


observations = {
    1: "red, orange, green",
    2: "Hot, dry",
    3: "lots of rocks"
}


SHARED_OBSERVATION_FILE = "shared_observations.txt"


MAX_REQUESTS = 1

def get_solution(problem_key, request_count):
    if request_count > MAX_REQUESTS:
        return "Request limit exceeded. Try fewer keys."
    return problems.get(problem_key, "No solution found")

def log_observation(rover_name, key, description):
    observations[key] = description
    with open(SHARED_OBSERVATION_FILE, "a") as f:
        f.write(f"{rover_name} - Observation {key}: {description}\n")

if __name__ == "__main__":

    log_observation("Rover1", 101, "Flat terrain, clear visibility")