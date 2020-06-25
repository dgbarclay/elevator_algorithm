import random
from tkinter import Tk, Canvas
from time import sleep
import copy

class Building:
    def __init__(self, floors, floor_dictionary, up_dictionary, down_dictionary):
        # floors of building
        self.floors = floors
        # total people per floor
        self.floor_dictionary = floor_dictionary
        # total people per floor with destination upwards
        self.up_dictionary = up_dictionary
        # total people per floor with destination below
        self.down_dictionary = down_dictionary

class Lift:
    def __init__(self, current_passengers, current_position, total_moves, passengers_remaining):
        # maximum number of people allowed onto lift at one time
        self.max_capacity = 10
        # list of passengers in lift with every index being a destination
        self.current_passengers = current_passengers
        # position of elevator, updated every movement
        self.current_position = current_position
        # counter of moves completed
        self.total_moves = total_moves
        # remaining passengers that have not been delivered
        self.passengers_remaining = passengers_remaining

def generateData(building, floors):
    """
    Generation of data. Includes people at each floor and their
    destination. Up to 5 people randomly generated for each floor.

    Parameters:
    building (obj): Building object
    floors (obj): Number of floors of building

    Returns:
    Building object populated with passengers

   """
    # initialize dictionaries
    floor_dictionary = {}
    up_dictionary = {}
    down_dictionary = {}
    i = 0
    # generates random number of people at each floor
    while i < floors:
        floor_dictionary[i] = random.randint(0,5)
        i += 1
    # allocates which passengers are going up and which are going down
    for key in floor_dictionary:
        counter_up = 0
        up_array = []
        counter_down = 0
        down_array = []

        # people at top floor cannot go up, bottom floor cannot go down.
        if key != (floors - 1) and key != 0:
            people_up = random.randint(0,floor_dictionary[key])
            people_down = floor_dictionary[key] - people_up
        elif key == 0:
            people_down = 0
            people_up = floor_dictionary[key]
        elif key == (floors - 1):
            people_down = floor_dictionary[key]
            people_up = 0

        #  assign random floor to people going up, above current floor
        while counter_up < people_up:
            up_array.append(random.randint(key+1, (floors-1)))
            counter_up += 1
        #  assign random floor to people going down, below current floor
        while counter_down < people_down:
            down_array.append(random.randint(0, key-1))
            counter_down += 1

        #  assign each array to dictionary for that key
        up_dictionary[key] = up_array
        down_dictionary[key] = down_array

    # update object with new values generated
    building = Building(floors, floor_dictionary, up_dictionary, down_dictionary)
    return building

def moveLift(total, building, lift, improved_algorithm):
    """
    Update the GUI with current lift statistics and move position of lift.

    Parameters:
    total (int): Total passengers delivered at floor
    building (obj): Building object
    lift (obj): Lift object
    improved_algorithm (Boolean): If improved algorithm is being run

    Returns:
    Updated GUI.

   """
    # GUI is inverted, must count from top
    draw_lift = building.floors - lift.current_position
    draw = 40 - 660/building.floors
    # improved algorithm is drawn to the left of original
    if improved_algorithm == True:
        xcoord_buffer = 500
        # update coordinates of lift on GUI
        w.coords(lift_draw_improved, 230 + xcoord_buffer, (draw + (660/building.floors)*draw_lift) + (660/building.floors),
        400 + xcoord_buffer, draw + (660/building.floors)*draw_lift )
    else:
        xcoord_buffer = 0
        w.coords(lift_draw, 230 + xcoord_buffer, (draw + (660/building.floors)*draw_lift) + (660/building.floors),
        400 + xcoord_buffer, draw + (660/building.floors)*draw_lift )

    # update remaining passengers
    lift.passengers_remaining = lift.passengers_remaining - total
    # update text
    text_current = w.create_text(100 + xcoord_buffer,10,fill="darkblue",font="Times 20 bold",
                        text="Total Moves: "+str(lift.total_moves))

    current_floor = w.create_text(100 + xcoord_buffer,70,fill="red",font="Times 20 bold",
                        text="Current Floor: "+str(lift.current_position))

    text_passengers = w.create_text(125 + xcoord_buffer,40,fill="darkblue",font="Times 20 italic bold",
                        text="Passengers Remaining: " + str(lift.passengers_remaining))

    text_delivered = w.create_text(125 + xcoord_buffer,100,fill="red",font="Times 20 italic bold",
                            text="Delivered at Floor: " + str(total))
    w.update()
    # remove text before next printing
    w.delete(text_current)
    w.delete(text_passengers)
    w.delete(current_floor)
    w.delete(text_delivered)

def printMoves(lift, improved_algorithm):
    """
    Update the GUI with final lift metrics.

    Parameters:
    lift (obj): Lift object
    improved_algorithm (Boolean): If improved algorithm is being run

    Returns:
    Updated GUI with final statistics.

   """
    # improved algorithm is drawn to the left of original
    if improved_algorithm == True:
        xcoord_buffer = 500
    else:
        xcoord_buffer = 0
    # update text with final stats
    w.create_text(100 + xcoord_buffer,10,fill="darkblue",font="Times 20 italic bold",
                        text="Total Moves: "+str(lift.total_moves))
    w.create_text(125 + xcoord_buffer,40,fill="darkblue",font="Times 20 italic bold",
                        text="All passengers delivered.")
    w.update()


def continueCheck(building, lift):
    """
    Check whether lift execution should continue.

    Parameters:
    building (obj): Building object
    lift (obj): Lift object

    Returns:
    True or False.

   """

    continue_lift = False
    # if passengers remain in any of the dictionaries, both same length.
    for i in range(0,len(building.up_dictionary),1):
        passengers = building.up_dictionary[i]
        if passengers:
            continue_lift = True
        else:
            continue
        passengers = building.down_dictionary[i]
        if passengers:
            continue_lift = True
        else:
            continue
    # any undelivered passengers, continue
    if (len(lift.current_passengers) > 0):
        continue_lift = True

    return continue_lift

def upElevator(start_position, building, lift, improved_algorithm):
    """
    Begins moving the lift upwards.

    Parameters:
    start_position (int): Starting floor of lift
    building (obj): Building object
    lift (obj): Lift object
    improved_algorithm (Boolean): If improved algorithm is being run

    Returns:
    Move elevator upwards.

   """
    # initialize position of lift
    lift.current_position = start_position

    while lift.current_position < (building.floors-1):
        total = 0
        # fill lift with people at floor
        if improved_algorithm == True:
            fillLiftImproved(lift, building, lift.current_position, 'up')
        else:
            fillLift(lift, building, lift.current_position)
        # sort passengers in lift by destination
        quickSort(lift.current_passengers, 0, len(lift.current_passengers)-1)
        continue_up = False
        # checks if lift is empty but people still require picking up
        if (len(lift.current_passengers) == 0 and improved_algorithm == True):
            for i in range(lift.current_position,len(building.up_dictionary),1):
                passengers = building.up_dictionary[i]
                if passengers:
                    continue_up = True
                passengers = building.down_dictionary[i]
                if passengers:
                    continue_up = True
        else:
            # if no one needs to go higher, turn around
            if len(lift.current_passengers) != 0:
                last_value = len(lift.current_passengers) - 1
                if (lift.current_passengers[last_value] > lift.current_position):
                    continue_up = True
                # search until target cannot be found
                while True:
                    index = binarySearch(lift.current_passengers, lift.current_position, len(lift.current_passengers)-1, 0)
                    if index != 'not found':
                        del lift.current_passengers[index]
                        total += 1
                    else:
                        break
        # fill lift with as many people capcity allows from current floor
        if improved_algorithm == True:
            fillLiftImproved(lift, building, lift.current_position, 'up')
        else:
            fillLift(lift, building, lift.current_position)
        # change coordinates of lift on GUI
        moveLift(total, building, lift, improved_algorithm)
        # Sleep to allow user to see movement on GUI
        sleep(0.1)
        # move lift up & add to total move counter
        lift.current_position += 1
        lift.total_moves += 1
        # check if all floors and current passengers on lift are empty
        continue_lift = continueCheck(building, lift)
        if continue_lift == False:
            # print final moves, terminate lift
            printMoves(lift, improved_algorithm)
            break
        # improved algorithm checks at every floor whether it should continue upwards
        if continue_up == False and improved_algorithm == True:
            # turn around before reaching top floor
            downElevator(building, lift, improved_algorithm)
            break

    continue_lift = continueCheck(building, lift)
    # lift turns around once top floor reached
    if continue_lift == True:
        downElevator(building, lift, improved_algorithm)


def downElevator(building, lift, improved_algorithm):
    """
    Begins moving the lift downwards.

    Parameters:
    building (obj): Building object
    lift (obj): Lift object
    improved_algorithm (Boolean): If improved algorithm is being run

    Returns:
    Moves the lift downwards.

   """

    start_position = lift.current_position
    while lift.current_position >= 0:
        total = 0
        # fill lift with people at current floor
        if improved_algorithm == True:
            fillLiftImproved(lift, building, lift.current_position, 'down')
        else:
            fillLift(lift, building, lift.current_position)
        # sort passengers in lift by destination
        quickSort(lift.current_passengers, 0, len(lift.current_passengers)-1)
        continue_down = False
        if (len(lift.current_passengers) == 0 and improved_algorithm == True):
            i = lift.current_position
            while i >= 0:
                passengers = building.down_dictionary[i]
                if passengers:
                    continue_down = True
                passengers = building.up_dictionary[i]
                if passengers:
                    continue_down = True
                i -= 1
        else:
            #  first element in list will always be lowest
            if len(lift.current_passengers) != 0:
                if (lift.current_passengers[0] < lift.current_position):
                    continue_down = True
                while True:
                    index = binarySearch(lift.current_passengers, lift.current_position, len(lift.current_passengers)-1, 0)
                    if index != 'not found':
                        del lift.current_passengers[index]
                        # counter for how many people removed at floor
                        total += 1
                    else:
                        break

        if improved_algorithm == True:
            fillLiftImproved(lift, building, lift.current_position, 'down')
        else:
            fillLift(lift, building, lift.current_position)

        moveLift(total, building, lift, improved_algorithm)
        sleep(0.1)
        # increment counters
        lift.current_position -= 1
        lift.total_moves += 1
        # check to terminate lift
        continue_lift = continueCheck(building, lift)
        if continue_lift == False:
            printMoves(lift, improved_algorithm)
            break
        if continue_down == False and improved_algorithm == True:
            # begins going up from floor above, prevents double delivery
            upElevator((lift.current_position+1),building, lift, improved_algorithm)
            break

    # once bottom floor is reached
    continue_lift = continueCheck(building, lift)
    if continue_lift == True:
        upElevator((lift.current_position+1), building, lift, improved_algorithm)

# fills lift with people at current floor
def fillLift(lift, building, current_position):
    """
    Populates the lift with passengers.

    Parameters:
    building (obj): Building object
    lift (obj): Lift object
    current_position (int): Current floor of lift

    Returns:
    Populated lift.

   """
    passengers = building.up_dictionary[current_position]
    # check if any passengers at that floor
    if passengers:
        for i in range(len(passengers)):
            # add passenger until floor empty or capacity reached
            destination = passengers[0]
            if len(lift.current_passengers) < lift.max_capacity:
                lift.current_passengers.append(destination)
                del passengers[0]
            else:
                continue
    passengers = building.down_dictionary[current_position]
    if passengers:
        for i in range(len(passengers)):
            destination = passengers[0]
            if len(lift.current_passengers) < lift.max_capacity:
                lift.current_passengers.append(destination)
                del passengers[0]
            else:
                continue

def fillLiftImproved(lift, building, current_position, direction):
    """
    Populates the lift with passengers with destination in the same
    direction as lift is travelling. Only used for improved algorithm.

    Parameters:
    building (obj): Building object
    lift (obj): Lift object
    current_position (int): Current position of lift
    direction (string): Direction of lift

    Returns:
    Filled lift.

    """
    if direction == 'up':
        passengers = building.up_dictionary[current_position]
    else:
        passengers = building.down_dictionary[current_position]
    # add passenger until floor empty or capacity reached
    if passengers:
        for i in range(len(passengers)):
            destination = passengers[0]
            if len(lift.current_passengers) < lift.max_capacity:
                lift.current_passengers.append(destination)
                del passengers[0]
            else:
                continue

def passengersRemaining():
    """
    Calculate passengers that have not been delivered.

    Returns:
    Total number of passengers undelivered.

   """
    passengers_remaining = 0
    # loop through both dictionaries and count all people
    for i in range(0,len(building.up_dictionary),1):
        passengers = building.up_dictionary[i]
        if passengers:
            passengers_remaining = passengers_remaining + len(passengers)
        else:
            continue
    for i in range(0,len(building.down_dictionary),1):
        passengers = building.down_dictionary[i]
        if passengers:
            passengers_remaining = passengers_remaining + len(passengers)
        else:
            continue

    return passengers_remaining

def binarySearch(array, target, high, low):
    """
    Search through passengers using binary search algorithm.

    Parameters:
    array (array): Array of current passengers
    target (int): Target value to be found
    high (int): Upper boundary
    low (int): Lower boundary

    Returns:
    Index of target.

   """
    # if upper bound is greater than lower bound, not in list.
    if high < low:
        return 'not found'
    else:
        middle = int(low + (high - low) / 2)
        # search to right of middle
        if array[middle] < target:
            low = middle + 1
            return binarySearch(array, target, high, low)
        # search to left of middle
        if array[middle] > target:
            high = middle - 1
            return binarySearch(array, target, high, low)
        # return position of target in list
        if array[middle] == target:
            return middle



def quickSort(array, first, last):
    """
    Quick sort for current passengers.

    Parameters:
    array (array): Array of passengers to be sorted
    first (int): Lower boundary
    last (int): Upper boundary

    Returns:
    Sorted array of passengers by destination.

   """
    # already sorted if array empty or 1 value
    if len(array) <= 1:
        return

    if first < last:
        # seperate array into partitions
        divide = partition(array, first, last)
        # keep partitioning recursively
        quickSort(array, first, divide - 1)
        quickSort(array, divide + 1, last)


def partition(array, first, last):
    """
    Generate pivot for seperating array.

    Parameters:
    array (array): Array of passengers to be sorted
    first (int): Lower boundary
    last (int): Upper boundary

    Returns:
    Pivoted array.

   """
    # partition up until final value
    pivot = array[last]
    i = first - 1

    for count in range(first, last):
        # split array
        if array[count] < pivot:
            i += 1
            # assign array positions
            array[i],array[count] = array[count],array[i]
    # reassign
    array[i+1],array[last] = array[last],array[i+1]
    return (i+1)

# create two identical buildings and two identical lifts to use in each algorithm.
building = Building(0, {}, {}, {})
building = generateData(building, 20)
duplicate_building = copy.deepcopy(building)
passengers_remaining = passengersRemaining()
passengers_remaining_duplicate = passengersRemaining()
lift = Lift([], 0, 0, passengers_remaining)
duplicate_lift = Lift([], 0, 0, passengers_remaining_duplicate)

# draw GUI
master = Tk()
w = Canvas(master, width=3000, height=3000)
w.pack()
w.create_rectangle(230, 40, 400, 700, width=2, outline = 'black')
w.create_rectangle(730, 40, 900, 700, width=2, outline = 'black')

# start position of the lift in GUI
lift_draw = w.create_rectangle(230, 700 - (660/building.floors), 400, 700, fill="red", outline = "red")
lift_draw_improved = w.create_rectangle(730, 700 - (660/building.floors), 900, 700, fill="blue", outline = "blue")
lift_drawer = 1
draw = 40
while lift_drawer < building.floors:
    # Where lift_drawer is the current floor.
    ANSWER = 660 / building.floors
    w.create_line(230, draw + (ANSWER * lift_drawer), 400, draw + (ANSWER * lift_drawer))
    w.create_line(730, draw + (ANSWER * lift_drawer), 900, draw + (ANSWER * lift_drawer))
    lift_drawer += 1

# execute both systems
upElevator(0, building, lift, False)
upElevator(0, duplicate_building, duplicate_lift, True)

# build GUI
master.mainloop()
