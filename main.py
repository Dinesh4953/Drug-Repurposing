from agents.master_agent import MasterAgent

def main():

    print("\n=== Pharma Innovation Discovery Agent ===\n")
    drug = input("Enter drug name: ").strip()

    agent = MasterAgent()
    agent.run(drug)


if __name__ == "__main__":
    main()
