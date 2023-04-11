from utilities.utils import animate_and_save, plt

fig, ax = plt.subplots(1, 1)

with open("/home/gg/scans.txt", 'r') as f:
    scans = eval(f.read())

animate_and_save(scans)