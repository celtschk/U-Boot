# get the colour names from X11's rgb.txt

rgbvalues = {}
with open("rgb.txt", "r") as rgbfile:
    for line in rgbfile:
        if line == "" or line[0] == '!':
            continue
        rgb, name = line.split('\t\t')
        rgbvalues[name.strip()] = tuple(int(value) for value in rgb.split())
