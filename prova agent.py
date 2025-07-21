
from dotenv import load_dotenv


# Load env
load_dotenv()
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "spiega in 100 parole un motore a flusso assiale")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.