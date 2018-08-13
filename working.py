import copy
import json
import math
import random
import sys
import tempfile

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter

color_black = (0, 0, 0, 255)
color_white = (255, 255, 255, 255)
offset = 10
POLYGONS = 50
poly_min_points = 3
poly_max_points = 5

class Polygon(object):
    def __init__(self, color=None, points=[]):
        self.color = color
        self.points = points

    def __str__ (self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return u"{}, {}".format(self.points, self.color)

    def mutate(self, size):
        rand = random.random()
        if rand <= 0.5:
            print (u"changing color")
            idx = random.randrange(0, 4)
            value = random.randrange(0, 256)
            color = list(self.color)
            color[idx] = value
            self.color = tuple(color)
        else:
            print (u"changing point")
            idx = random.randrange(0, len(self.points))
            point = generate_point(size[0], size[1])
            self.points[idx] = point

class DNA(object):
    def __init__(self, img_size, polygons=[]):
        self.img_size = img_size
        self.polygons = polygons
        self.generation = 0

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return (u"{}".format(self.polygons))

    def print_polygons(self):
        for polygon in self.polygons:
            print (polygon)

    def draw(self, background=color_black, show=False, save=False, generation=None):
        size = self.img_size
        img = Image.new('RGB', size, background)
        draw = Image.new('RGBA', size)
        pdraw = ImageDraw.Draw(draw)
        for polygon in self.polygons:
            color = polygon.color
            points = polygon.points
            pdraw.polygon(points, fill=color, outline=color)
            img.paste(draw, mask=draw)

        if show:
            img.show()

        if save:
            temp_dir = tempfile.gettempdir()
            temp_name = (u"000000000{}".format(generation)[-10:])
            out_path = (u"{}/{}.png".format(temp_dir, temp_name))
            img = img.filter(ImageFilter.GaussianBlur(radius=3))
            img.save(out_path)
            print (u"saving image to {}".format(out_path))

        return img

    def mutate(self):
        polygons = copy.deepcopy(self.polygons)
        rand = random.randrange(0, len(polygons))
        random_polygons = polygons[rand]
        random_polygons.mutate(self.img_size)

        return DNA(self.img_size, polygons)

def fitness(img_1, img_2):
    fitness = 0.0
    for y in range(0, img_1.size[1]):
        for x in range (0, img_1.size[0]):
            r1, g1, b1 = img_1.getpixel((x, y))
            r2, g2, b2 = img_2.getpixel((x, y))

            d_r = r1 - r2
            d_b = b1 - b2
            d_g = g1 - g2

            pixel_fitness = math.sqrt(d_r * d_r + d_g * d_g + d_b * d_b)

            fitness += pixel_fitness
    return fitness

def generate_point(width, height):
    x = random.randrange(0 - offset, width + offset, 1)
    y = random.randrange(0 - offset, height + offset, 1)
    return (x, y)

def generate_color():
    red = random.randrange(0, 256)
    green = random.randrange(0, 256)
    blue = random.randrange(0, 256)
    alpha = random.randrange(0, 256)
    return (red, green, blue, alpha)

def generate_dna(img_size, dna_size=POLYGONS, fixed_color=False):
    dna = None
    polygons = []
    (width, height) = img_size

    for i in range(POLYGONS):
        nr_of_points = random.randrange(poly_min_points, poly_max_points + 1)
        points = []
        for j in range(nr_of_points):
            point = generate_point(width, height)
            points.append(point)

        color = color_white if fixed_color else generate_color()
        polygon = Polygon(color, points)
        polygons.append(polygon)

    dna = DNA(img_size, polygons)
    return dna

def load_image(path):
    img = Image.open(path)
    return img

def main(argv):
    if len(argv) != 2:
        sys.exit(0)

    path = argv[1]
    img = load_image(path)
    img_size = img.size
    dna = generate_dna(img_size, dna_size=POLYGONS, fixed_color=True)
    parent = dna.draw(show=False)
    fitness_parent = fitness(img, parent)

    generations = pic_nr = 0
    while True:
        dna_mutated = dna.mutate()
        child = dna_mutated.draw()
        fitness_child = fitness(img, child)
        if fitness_child < fitness_parent:
            dna = dna_mutated
            fitness_parent = fitness_child
            print (u"picking child w. fitness: {}".format(fitness_child))

        generations += 1
        if generations % 100 == 0:
            print (u"showing generation {}".format(generations))
            pic_nr += 1
            dna.draw(show=False, save=True, generation=pic_nr)

    return sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)















