from numpy import sqrt, arctan, cos, sin, degrees, radians, arange, random
from matplotlib import pyplot as plt, colors as mcolors, use
try:
    use("Qt5Agg")
except ImportError:
    pass
except ValueError:
    pass


class Vector:
    def __init__(self, vector: [float, float] = None, components: [float, float] = None):
        if vector is not None:
            self.vector = vector
            self._get_components()
        elif components is not None:
            self.components = components
            self._get_vector()
        else:
            raise ValueError("Must provide either a vector or components")

        self.x = self.components[0]
        self.y = self.components[1]
        self.magnitude = self.vector[0]
        self.angle = self.vector[1]

    def _get_components(self):
        if self.vector is not None:
            x = self.vector[0]*cos(radians(self.vector[1]))
            y = self.vector[0]*sin(radians(self.vector[1]))
            self.components = [round(x, 5), round(y, 5)]

    def _get_vector(self):
        if self.components is not None:
            magnitude = sqrt(self.components[0]**2 + self.components[1]**2)
            angle = degrees(arctan(self.components[1]/self.components[0]))
            self.vector = [round(magnitude, 5), round(angle, 5)]

    def get_components(self, vector):
        x = vector[0]*cos(radians(vector[1]))
        y = vector[0]*sin(radians(vector[1]))
        return Vector(None, [round(x, 5), round(y, 5)])

    def get_vector(self, components):
        magnitude = sqrt(components[0]**2 + components[1]**2)
        angle = degrees(arctan(components[1]/components[0]))
        return Vector([round(magnitude, 5), round(angle, 5)])

    def rotate(self, angle):
        result = self.vector[1] + angle
        if result > 360:
            result -= 360
        elif result < 0:
            result += 360
        self.vector[1] = result

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(None, [self.components[0] + other.components[0], self.components[1] + other.components[1]])
        else:
            raise TypeError("Can only add vectors")

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(None, [self.components[0] - other.components[0], self.components[1] - other.components[1]])
        else:
            raise TypeError("Can only subtract vectors")

    def __str__(self):
        return f"Vector: {self.vector}, Components: {self.components}"

    def __repr__(self):
        return f"Vector: {self.vector}, Components: {self.components}"


def plot_cartesian(x, y, ax, arrow=True, xy_lines=True, vec_lines=True, sep_text=True, line_thickness=1.5, color=None):

    # Make resultant vector the last one on the list
    # Select length of axes and the space between tick labels
    try:
        xmin, xmax, ymin, ymax = -max([abs(i) for i in x]), max([abs(i) for i in x]), \
            -max([abs(i) for i in y]), max([abs(i) for i in y])
    except:
        xmin, xmax, ymin, ymax = -max([abs(i) for i in x]+[5]), max([abs(i) for i in x]+[5]), -max([abs(i) for i in y]+[5]), max([abs(i) for i in y]+[5])
    #xmin, xmax, ymin, ymax = -15, 15, -15, 15
    ticks_frequency = ((xmax/10)+(ymax/10))/2
    color_list = list(mcolors.BASE_COLORS.keys())
    color_list.remove("g")
    color_list.remove("w")
    colors = [color_list[i % len(color_list)] for i in range(len(x))]
    colors[-1] = "g"


    # Plot points
    ax.scatter(x, y, c=color, s=plt.rcParams["lines.markersize"]) if not arrow else None

    # Draw lines connecting points to axes
    for x, y, c in zip(x, y, colors):
        if color:
            c = color
        ax.plot([x, x], [0, y], c=c, ls='--', lw=line_thickness, alpha=0.5) if xy_lines else None
        ax.plot([0, x], [y, y], c=c, ls='--', lw=line_thickness, alpha=0.5) if xy_lines else None
        ax.plot([0, x], [0, y], c=c, ls='-', lw=line_thickness, alpha=0.5)  if vec_lines else None
        plt.arrow(0, 0, x, y, head_width=0.15, head_length=0.3, fc=c, ec=c) if arrow else None

    # Set identical scales for both axes
    try:
        ax.set(xlim=(xmin - 1, xmax + 1), ylim=(ymin - 1, ymax + 1), aspect='equal')
    except ValueError:
        print("Range Error.F")
        ax.set(xlim=(-15, 15), ylim=(-15, 15))

    # Set bottom and left spines as x and y axes of coordinate system
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_position('zero')

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Create 'x' and 'y' labels placed at the end of the axes
    ax.set_xlabel('x', size=14, labelpad=-24, x=1.03)
    ax.set_ylabel('y', size=14, labelpad=-21, y=1.02, rotation=0)

    if sep_text:
        # Create custom major ticks to determine position of tick labels
        x_ticks = arange(xmin, xmax + 1, ticks_frequency)
        y_ticks = arange(ymin, ymax + 1, ticks_frequency)
        ax.set_xticks(x_ticks[x_ticks != 0])
        ax.set_yticks(y_ticks[y_ticks != 0])

        # Create minor ticks placed at each integer to enable drawing of minor grid
        # lines: note that this has no effect in this example with ticks_frequency=1
        ax.set_xticks(arange(xmin, xmax + 1), minor=True)
        ax.set_yticks(arange(ymin, ymax + 1), minor=True)

    # Draw major and minor grid lines
    ax.grid(which='both', color='grey', linewidth=1, linestyle='-', alpha=0.2)

    # Draw arrows
    arrow_fmt = dict(markersize=4, color='black', clip_on=False)
    ax.plot(1, 0, marker='>', transform=ax.get_yaxis_transform(), **arrow_fmt)
    ax.plot(0, 1, marker='^', transform=ax.get_xaxis_transform(), **arrow_fmt)