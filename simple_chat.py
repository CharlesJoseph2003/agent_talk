import time
from openai import OpenAI
import os
import random
from datetime import datetime
import json
import tiktoken
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI client
client = OpenAI()  # OpenAI automatically reads from OPENAI_API_KEY environment variable

# Configure tokenizer for measuring message length
tokenizer = tiktoken.get_encoding("cl100k_base")

class ConversationLogger:
    def __init__(self, filename):
        self.filename = filename
        self.conversation = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Rover Low-Bandwidth Communication",
            "messages": [],
            "transmission_stats": {
                "total_tokens_sent": 0,
                "transmission_success": True,
                "transmission_errors": 0
            }
        }
    
    def log(self, rover_id, message, token_count=None):
        message_obj = {
            "rover_id": rover_id,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "token_count": token_count if token_count else len(tokenizer.encode(message))
        }
        
        self.conversation["messages"].append(message_obj)
        self.conversation["transmission_stats"]["total_tokens_sent"] += message_obj["token_count"]
        self._save_conversation()
    
    def set_outcome(self, transmission_success, errors=0):
        self.conversation["transmission_stats"] = {
            "total_tokens_sent": self.conversation["transmission_stats"]["total_tokens_sent"],
            "transmission_success": transmission_success,
            "transmission_errors": errors
        }
        self._save_conversation()
    
    def _save_conversation(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation, f, indent=2)

class RoverAgent:
    def __init__(self, rover_id, mission_objective, location, data_priority):
        self.rover_id = rover_id
        self.mission_objective = mission_objective
        self.conversation_history = []
        self.location = location
        self.data_priority = data_priority
        self.max_tokens_per_message = 7  # Ultra low bandwidth constraint - 1 tokens per message
        
    def get_response(self, message, other_rover_id):
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": f"{other_rover_id}: {message}"})
        
        # Create mission context
        mission_context = f"You are Rover {self.rover_id} at location {self.location}. Your mission objective is: {self.mission_objective}. Your priority data types are: {self.data_priority}."
        
        # Create the system prompt with ultra low bandwidth constraint
        system_prompt = f"{mission_context}\n\nIMPORTANT: You are operating under EXTREME bandwidth limitations. Your response MUST be 7 TOKENS OR LESS - NO EXCEPTIONS. Use abbreviations & remove all unnecessary words. This is a strict constraint for ultra-low bandwidth interplanetary communication. Each word/number typically counts as one token. There is NO total token limit across messages.\n\nYou can end the communication when appropriate by including words like 'complete', 'done', 'finished', 'end', or 'over' in your message."
        
        # Prepare the messages for API call
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 4 exchanges to stay within context limits)
        messages.extend(self.conversation_history[-8:])
        
        try:
            # Make API call to get response
            print(f"Requesting response from Rover {self.rover_id}...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using gpt-3.5-turbo for faster responses
                messages=messages,
                temperature=0.7,
                max_tokens=20  # Smaller max_tokens for faster responses
            )
            reply = response.choices[0].message.content
            print(f"Response received from API call.")
            
            # Check token count and truncate if necessary
            token_count = len(tokenizer.encode(reply))
            if token_count > self.max_tokens_per_message:
                print(f"Warning: Response exceeded limit of {self.max_tokens_per_message} tokens ({token_count}). Truncating...")
                # Simply truncate to the token limit - no need for sentence boundaries with such short messages
                token_ids = tokenizer.encode(reply)[:self.max_tokens_per_message]
                reply = tokenizer.decode(token_ids)
                
                # Get new token count after truncation
                token_count = len(tokenizer.encode(reply))
            
            # Add the response to conversation history
            self.conversation_history.append({"role": "assistant", "content": reply})
            
            # No need to track total token usage
            
            return reply, token_count
            
        except Exception as e:
            print(f"Error: {e}")
            error_message = "ERROR"  # Shorter error message (1 token)
            error_tokens = len(tokenizer.encode(error_message))
            # Simple error handling
            return error_message, error_tokens

def analyze_communication_success(messages):
    # Initialize with default values
    outcome = {
        "transmission_success": True,
        "error_count": 0,
        "data_transferred": sum(msg.get("token_count", 0) for msg in messages),
        "reason": "Communication completed successfully."
    }
    
    # Check for transmission errors
    error_messages = [msg for msg in messages if "ERROR" in msg.get("message", "").upper()]
    outcome["error_count"] = len(error_messages)
    
    # Check if any message exceeded token limit
    oversized_messages = [msg for msg in messages if msg.get("token_count", 0) > 50]
    
    # Determine the outcome
    if outcome["error_count"] > 0:
        outcome["transmission_success"] = False
        outcome["reason"] = f"Communication experienced {outcome['error_count']} transmission errors."
    elif oversized_messages:
        outcome["transmission_success"] = True  # Still successful but with warnings
        outcome["reason"] = f"Communication completed with {len(oversized_messages)} messages that required truncation."
    
    return outcome

def run_communication(rover1, rover2, logger=None):
    print(f"\n===== Starting Ultra-Low-Bandwidth Communication =====\n")
    print(f"Constraint: Strictly 1 tokens per message maximum (no total limit)")
    print(f"Rover {rover1.rover_id} at {rover1.location}")
    print(f"Rover {rover2.rover_id} at {rover2.location}\n")
    
    # First message from rover1
    is_rover1_turn = True
    initial_message = "Status report?"  # Starting with a very short message (2 tokens)
    initial_tokens = len(tokenizer.encode(initial_message))
    
    print(f"Rover {rover1.rover_id} [{initial_tokens} tokens]: {initial_message}")
    
    if logger:
        logger.log(rover1.rover_id, initial_message, initial_tokens)
    
    # Current message for the conversation flow
    current_message = initial_message
    
    # Keep track of all messages for analysis
    all_messages = [{"rover_id": rover1.rover_id, "message": current_message, "token_count": initial_tokens}]
    
    # Loop until conversation naturally concludes
    max_turns = 20  # Safety limit to prevent infinite loops
    turn_count = 0
    
    while turn_count < max_turns:
        turn_count += 1
        time.sleep(1)  # Add a small delay for readability
        
        # Check for conversation completion keywords in the last message
        if turn_count > 1 and any(keyword in current_message.lower() for keyword in ["complete", "done", "finished", "end", "over", "mission complete"]):
            print("\nDetected conversation completion signal. Communication ending.")
            break
        
        # Get response based on whose turn it is
        if is_rover1_turn:
            # It's rover2's turn to respond
            current_message, token_count = rover2.get_response(current_message, rover1.rover_id)
            sender = rover2.rover_id
            is_rover1_turn = False
        else:
            # It's rover1's turn to respond
            current_message, token_count = rover1.get_response(current_message, rover2.rover_id)
            sender = rover1.rover_id
            is_rover1_turn = True
        
        # Print with token count (highlight if exceeds limit)
        if token_count > 7:
            print(f"Rover {sender} [{token_count} tokens - EXCEEDS LIMIT!]: {current_message}")
        else:
            print(f"Rover {sender} [{token_count} tokens]: {current_message}")
        all_messages.append({"rover_id": sender, "message": current_message, "token_count": token_count})
        
        # Log the message if logger is provided
        if logger:
            logger.log(sender, current_message, token_count)
    
    # Analyze the outcome of the communication
    outcome = analyze_communication_success(all_messages)
    if logger:
        if outcome["transmission_success"]:
            print(f"\nCommunication completed with {outcome['data_transferred']} total tokens across {turn_count} turns.")
            print(f"Reason: {outcome['reason']}")
            logger.set_outcome(True, outcome['error_count'])
        else:
            print("\nCommunication experienced errors.")
            print(f"Reason: {outcome['reason']}")
            logger.set_outcome(False, outcome['error_count'])
    else:
        if turn_count >= max_turns:
            print("\nMaximum turn limit reached - communication ended.")
        else:
            print("\nCommunication completed naturally.")

def main():
    # Create Rover 1 - Exploration Rover
    exploration_rover = RoverAgent(
        rover_id="R1-EXPL",
        mission_objective="Survey western valley for geological samples and water evidence",
        location="Western Valley Sector 7",
        data_priority="Geological samples, water detection, terrain mapping"
    )
    
    # Create Rover 2 - Science Rover
    science_rover = RoverAgent(
        rover_id="R2-SCI",
        mission_objective="Analyze soil samples and atmospheric conditions in the eastern ridge",
        location="Eastern Ridge Base", 
        data_priority="Soil composition, atmospheric readings, radiation levels"
    )
    
    # Create a logger
    logger = ConversationLogger("conversation_log.json")
    
    # Run the communication without a fixed turn limit
    run_communication(exploration_rover, science_rover, logger=logger)

if __name__ == "__main__":
    main()
