import os 
import json 
import time 
import random 

def sim_processing_file(id):
    """
    Simulates processing a file. 
    """

    print(f"Simulating processing file with id {id}...")

    time.sleep(random.randint(1,120))

    print(f"Finished processing file with id {id}")


def main():
    queue_message = os.getenv("QUEUE_MESSAGE")
    try:
        msg_json = json.loads(queue_message)
    except:
        print(f"Couldn't load environnment variable QUEUE_MESSAGE")
        return 
    
    # Try to access secrets stored in kubernetes
    secret_abc = os.getenv("ABC_SECRET")
    print(f"ABC_SECRET value: {secret_abc}")

    secret_def = os.getenv("DEF_SECRET")
    print(f"DEF_SECRET value: {secret_def}")



    print(f"Received Message JSON through env var with id {msg_json['id']}")
    
    print(f"Retrieving file for id {msg_json['id']}")
    time.sleep(random.randint(1,5))

    sim_processing_file(msg_json['id'])

    print(f"Pushing resulting file for id {msg_json['id']}")
    time.sleep(random.randint(1,5))

    print(f"done")
    

if __name__ == "__main__":
    main()

