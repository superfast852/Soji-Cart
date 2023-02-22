# TODO: Create an algorithm that calculates the curve needed to avoid the obstacle (Optional, yet Optimal)
from itertools import groupby
from operator import itemgetter
from _pickle import load
from numpy import shape


def check_collision(ranges, collision_range, threshold):
    for vec in ranges[collision_range[0]:collision_range[1]]: # for every vector in the collision range
        if vec > threshold: # if the vector is greater than the threshold
            pass # go to next vector
        else:  # if the vector is less than the threshold
            return True  # an obstacle has been detected
    else:
        return False  # if the for loop completes, no obstacles were detected


def check_surroundings(ranges, threshold):
    ls_clear = []
    rs_clear = []

    for i, distance in enumerate(ranges[90:180]):  # Right Side Check
        if distance > threshold:  # If the vector_distance is greater than the threshold
            rs_clear.append(i+90)  # append the angle of the vector to the list of available angles angles

    for i, distance in enumerate(ranges[180:270]):  # Left Side Check
        if distance > threshold:
            ls_clear.append(i+180)

    # From the list, extract all numerical sequences (e.g. [3, 5, 1, 2, 3, 4, 5, 8, 3, 1] -> [[1, 2, 3, 4, 5]])
    ls_sequences = _extract_sequence(ls_clear)
    rs_sequences = _extract_sequence(rs_clear)

    # Find the longest sequence, as there might be multiple sequences.
    # If there were no sequences, the longest sequence would be 0.
    ls_space = max(ls_sequences, key=len) if len(ls_sequences) > 0 else [0, 0]
    rs_space = max(rs_sequences, key=len) if len(rs_sequences) > 0 else [0, 0]

    if len(ls_space) > len(rs_space):  # If the left side has more space
        return "Left", ls_space  # Return the direction and the angles of the obstacle for future optional odometry.
    else:  # If the right side has more space
        return "Right", rs_space  # Return the direction and the angles of the obstacle for future optional odometry.


def _extract_sequence(array):
    sequences = []
    for k, g in groupby(enumerate(array), lambda x: x[0] - x[1]):
        seq = list(map(itemgetter(1), g))
        sequences.append(seq) if len(seq) > 1 else None
    return sequences


if __name__ == "__main__":

    collision_space = 1
    collision_bounds = (180 - (collision_space // 2), 180 + (collision_space // 2))
    collision_threshold = 4

    with open("scans.pkl", "rb") as f:
        scans = load(f)
        print(f"scans.pkl loaded. shape: {shape(scans)}")

    for scan in scans:
        # Dead Scan Check
        if scan.count(0) > 10:
            print("Invalid scan.")
            continue

        if check_collision(scan, collision_bounds, collision_threshold):  # Check for collision in front

            direction, angles = check_surroundings(scan, collision_threshold)  # Get the clearest lateral path
            print(f"{direction} side clear. {len(angles)} degrees available.")

        else:
            print("Forward clear.")
