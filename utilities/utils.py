from os import environ, getcwd
from matplotlib.animation import FFMpegWriter, FuncAnimation as anim
from _pickle import dump, load
from utilities.pyvec import plot_cartesian, Vector, plt
from time import time
from math import pi, sin, cos, radians





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


def _anim_lidar(i, ax, scans, bounds=(0, 360), collision_bounds=None, amplification=1):
    x = [0]*360
    y = [0]*360
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


def update_rtp(x, y, ax):
    ax.clear()
    plot_cartesian(x, y, ax, 0, 0, 0, 0, color="b")
    plt.pause(0.000001)
    plt.draw()


def op_time(prev_time=0):
    return time() - prev_time


def point_pos(d, theta):
    theta_rad = pi/2 - radians(theta)
    return d*cos(theta_rad), d*sin(theta_rad)


def plot(data, ax, mask=(0, 0)):
    x = []
    y = []
    for angle, distance in enumerate(data[mask[0]:mask[1]]):
        point = point_pos(distance, angle)
        x.append(point[0])
        y.append(point[1])
    update_rtp(x, y, ax)
