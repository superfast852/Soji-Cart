from os import environ, getcwd
from matplotlib.animation import FFMpegWriter, FuncAnimation as anim
from _pickle import dump, load
from utilities.pyvec import *
from time import time


def smoothSpeed(current, target, speed_lim=1, min_speed=0.1, smoothing_spread=10):
    distance = current-target
    try:
        direction = -distance/abs(distance)
        speed = min(9, (distance/10)**2/smoothing_spread)
        output = (1+speed)*direction/10*speed_lim
        return output if abs(output) > min_speed else min_speed*direction
    except ZeroDivisionError:
        return 0


def set_environment():
    print(getcwd())
    environ["WEBOTS_HOME"] = "/snap/webots/24/usr/share/webots"
    environ["PYTHONPATH"] = "/snap/webots/24/usr/share/webots/lib/controller/python"
    environ["PYTHONIOENCODING"] = "UTF-8"


def _save_scan(scan, animation, filename="scans", format="mp4", fps=30):
    # Pickle save
    with open(f"{filename}.pkl", "wb") as f:
        dump(scan, f)
    print("Saved pickle file.")
    # Video save
    writer = FFMpegWriter(fps=fps)
    animation.save(f"{filename}.{format}", dpi=600, writer=writer,
                   progress_callback=lambda i, n: print(f'Saving frame {i} of {n}'))
    print("Saved video file.")
    return 1


x = [0]*360
y = [0]*360


def _anim_lidar(i, ax, scans, bounds=(0, 360), collision_bounds=None, amplification=1):
    ax.clear()
    scan = scans[i]
    vectors = [Vector([magnitude*amplification, angle-90]) for angle, magnitude in enumerate(scan)]
    for i, vector in enumerate(vectors):
        x[i], y[i] = vector.components

    if collision_bounds is not None:
        plot_cartesian(x[collision_bounds[0]:collision_bounds[1]],
                       y[collision_bounds[0]:collision_bounds[1]], ax, 0,0,0,0, color="r")

        plot_cartesian(x[bounds[0]:collision_bounds[0]], y[bounds[0]:collision_bounds[0]], ax, 0, 0, 0, 0, color="b")
        plot_cartesian(x[collision_bounds[1]:bounds[1]], y[collision_bounds[1]:bounds[1]], ax, 0, 0, 0, 0, color="b")
    else:
        plot_cartesian(x[bounds[0]:bounds[1]], y[bounds[0]:bounds[1]], ax, 0, 0, 0, 0)


def animate_and_save(scans, amplification=1, mask=(0, 360), bounds=None, filename="scans"):
    fig, ax = plt.subplots(1, 1)
    if isinstance(scans, str) and scans.endswith(".pkl"):
        with open(scans, "rb") as f:
            scans = load(f)

    animation = anim(fig, _anim_lidar, frames=len(scans), repeat=False, fargs=(ax, scans, mask, bounds, amplification))
    _save_scan(scans, animation, filename=filename)
    print(f"Done! Saved at {filename}")


def update_rtp(args):
    scan, ax = args
    ax.clear()
    vectors = [Vector([distance, angle]) for angle, distance in enumerate(scan)]

    x = [vector.x for vector in vectors]
    y = [vector.y for vector in vectors]

    plot_cartesian(x, y, ax, 0, 0, 0, 0, color="b")
    plt.pause(0.000001)
    plt.draw()


def op_time(prev_time=0):
    return time() - prev_time
