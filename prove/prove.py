"""
Course: CSE 251
Lesson Week: 10
File: assignment.py
Author: Caleb Packer

Purpose: assignment for week 10 - reader writer problem

Instructions:

- Review TODO comments

- writer: a process that will send numbers to the reader.  
  The values sent to the readers will be in consecutive order starting
  at value 1.  Each writer will use all of the sharedList buffer area
  (ie., BUFFER_SIZE memory positions)

- reader: a process that receive numbers sent by the writer.  The reader will
  accept values until indicated by the writer that there are no more values to
  process.  

- Do not use try...except statements

- Display the numbers received by the reader printing them to the console.

- Create WRITERS writer processes

- Create READERS reader processes

- You can NOT use sleep() statements.

- You are able (should) to use lock(s) and semaphores(s).  When using locks, you can't
  use the arguments "block=False" or "timeout".  Your goal is to make your
  program as parallel as you can.  Over use of lock(s), or lock(s) in the wrong
  place will slow down your code.

- You must use ShareableList between the two processes.  This shareable list
  will contain different "sections".  There can only be one shareable list used
  between your processes.
  1) BUFFER_SIZE number of positions for data transfer. This buffer area must
     act like a queue - First In First Out.
  2) current value used by writers for consecutive order of values to send
  3) Any indexes that the processes need to keep track of the data queue
  4) Any other values you need for the assignment

- Not allowed to use Queue(), Pipe(), List(), Barrier() or any other data structure.

- Not allowed to use Value() or Array() or any other shared data type from 
  the multiprocessing package.

- When each reader reads a value from the sharedList, use the following code to display
  the value:
  
                    print(<variable from the buffer>, end=', ', flush=True)

Add any comments for me:

"""

import random
from multiprocessing.managers import SharedMemoryManager
import multiprocessing as mp

BUFFER_SIZE = 10
READERS = 2
WRITERS = 2

def main():

    # This is the number of values that the writer will send to the reader
    items_to_send = random.randint(1, 10) #change back to 1000, 10000

    smm = SharedMemoryManager()
    smm.start()

    # TODO - Create a ShareableList to be used between the processes
    #      - The buffer should be size 10 PLUS at least three other
    #        values (ie., [0] * (BUFFER_SIZE + 3)).  The extra values
    #        are used for the head and tail for the circular buffer.
    #        The another value is the current number that the writers
    #        need to send over the buffer.  This last value is shared
    #        between the writers.
    #        You can add another value to the sharedable list to keep
    #        track of the number of values received by the readers.
    #        (ie., [0] * (BUFFER_SIZE + 4))
    shared_list = smm.ShareableList([0] * (BUFFER_SIZE + 6))

    # Initialize metadata
    shared_list[BUFFER_SIZE] = 0  
    shared_list[BUFFER_SIZE + 1] = 0  
    shared_list[BUFFER_SIZE + 2] = 1  
    shared_list[BUFFER_SIZE + 3] = 0  
    shared_list[BUFFER_SIZE + 4] = 0  
    shared_list[BUFFER_SIZE + 5] = 0 

    # TODO - Create any lock(s) or semaphore(s) that you feel you need
    lock = mp.Lock()
    empty_slots = mp.Semaphore(BUFFER_SIZE)
    filled_slots = mp.Semaphore(0)

    # TODO - create reader and writer processes
    writers = [mp.Process(target=writer, args=(shared_list, empty_slots, filled_slots, lock, items_to_send))
               for _ in range(WRITERS)]
    readers = [mp.Process(target=reader, args=(shared_list, empty_slots, filled_slots, lock, items_to_send))
               for _ in range(READERS)]

    # TODO - Start the processes and wait for them to finish
    for p in writers + readers:
        p.start()

    for p in writers + readers:
        p.join()

    # TODO - Display the number of numbers/items received by the reader.
    #        Can not use "items_to_send", must be a value collected
    #        by the reader processes.
    # print(f'{<your variable>} values received')
    # print(f'\n{items_to_send} values sent')
    print(f'{shared_list[BUFFER_SIZE + 4]} values received')

    smm.shutdown()

def writer(shared_list, empty_slots, filled_slots, lock, items_to_send):
    for _ in range(items_to_send):  # Loop to send all items
        empty_slots.acquire()  # Wait for an empty slot

        with lock:
            # Generate the next number to send
            number = shared_list[BUFFER_SIZE + 2]
            shared_list[BUFFER_SIZE + 2] += 1  # Increment the next value to send
            
            # Write to the buffer
            tail = shared_list[BUFFER_SIZE + 1]
            shared_list[tail] = number
            shared_list[BUFFER_SIZE + 1] = (tail + 1) % BUFFER_SIZE  # Update tail pointer
            shared_list[BUFFER_SIZE + 3] += 1  # Increment items sent

        filled_slots.release()  # Signal an item is available

    with lock:
        shared_list[BUFFER_SIZE + 5] += 1


def reader(shared_list, empty_slots, filled_slots, lock, items_to_send):
    while True:
        filled_slots.acquire()  # Wait for an item to be available

        with lock:
            # Check if all items have been received
            if shared_list[BUFFER_SIZE + 5] == 1 and shared_list[BUFFER_SIZE+4] >= items_to_send:
                break

            # Read from the buffer
            head = shared_list[BUFFER_SIZE]
            number = shared_list[head]
            shared_list[BUFFER_SIZE] = (head + 1) % BUFFER_SIZE  # Update head pointer
            shared_list[BUFFER_SIZE + 4] += 1  # Increment items received

        empty_slots.release()  # Signal an empty slot
        # print(number, end=', ', flush=True)
      


if __name__ == '__main__':
    main()
