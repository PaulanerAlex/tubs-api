import zenoh
import time
import datetime

with zenoh.open(zenoh.Config()) as session:
    key = "clara/from_remote" # TODO: paramereize
    pub = session.declare_publisher(key)
    running = True
    num = 0 
    while running:
        msg = f"Hello World: {str(num)}"
        print(f"Publishing: {msg}")
        pub.put(msg)
        time.sleep(1)
        num += 1
        if num > 1000000000:
            running = False
