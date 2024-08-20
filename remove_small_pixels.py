from PIL import Image, ImageFilter, ImageFont, ImageDraw
import numpy as np
import time
from skimage.filters.rank import majority
from skimage.morphology import square
import random

def smooth(mat):
    for _ in range(2):
        for _ in range(5):
            mat = majority(mat, square(3))
        mat = majority(mat, square(5))
    return mat
    

def outline(mat):
    shift_up = np.roll(mat, 1, axis=0)
    shift_right = np.roll(mat, 1, axis=1)
    shift_up[0, :] = mat[0, :]
    shift_right[:, 0] = mat[:, 0]

    outline_im = np.logical_and(mat == shift_up, mat == shift_right)

    # outline_im = np.logical_and(np.logical_or((mat == shift_up),(shift_up == -1)),np.logical_or((mat == shift_right),(shift_right == -1)))
    return np.stack((np.where(outline_im, 255, 200),)*3, axis=-1).astype(np.uint8)


def get_position(r, c, mat):
    height, width = mat.shape[0], mat.shape[1]
    colour = mat[c][r]
    i = 0
    while r+i < width and mat[c][r+i] == colour:
        i += 1
    j = 0
    while c+j < height and mat[c+j][r] == colour:
        j += 1
    k = 0
    while r+k < width and c+k < height and mat[c+k][r+k] == colour:
        k += 1

    if i > j and i > k:
        return (r + (i // 2), c)
    elif j > i and j > k:
        return (r, c + (j // 2))
    else:
        return (r + (k // 2), c + (k // 2))


def get_regions(mat):
    height, width = mat.shape[0], mat.shape[1]

    regions = np.zeros(mat.shape, dtype=int)
    discovered = np.full(mat.shape, False)
    
    def dfs(r, c, region):
        stack = [(r, c)]
        colour = mat[c][r]
        while stack != []:
            row, col = stack.pop()
            if row >= 0 and row < width and col >= 0 and col < height:
                if mat[col][row] == colour:
                    if not discovered[col][row]:
                        regions[col][row] = region
                        discovered[col][row] = True
                        stack.append((row+1, col))
                        stack.append((row-1, col))
                        stack.append((row, col+1))
                        stack.append((row, col-1))

    number_positions = []

    region = 0
    for r in range(width):
        for c in range(height):
            if not discovered[c][r]:
                dfs(r, c, region)
                number_positions.append((get_position(r, c, mat), mat[c][r]))
                region += 1
    return number_positions
    # return regions, number_positions

def generate_color(): 
  # Generate random values for red, green, and blue 
  r = random.randint(0, 255) 
  g = random.randint(0, 255) 
  b = random.randint(0, 255) 
 
  
  return [r, g, b] 

def draw_point(mat, i, j, colour):
    if i >= 0 and i < len(mat) and j >= 0 and j < len(mat[0]):
        mat[i][j][0] = colour[0]
        mat[i][j][1] = colour[1]
        mat[i][j][2] = colour[2]

def draw_numbers(mat, positions, text_colour):
    digit_map = {
        0: [(-1, -2), (1, -2), (-1, -1), (1, -1), (-1, 0), (+1, 0), (-1, 1), (1, 1), (-1, 2), (1, 2), (0, 2), (0, -2)],
        1: [(0,-2), (0,-1), (0,0), (0,1), (0,2), (-1,-1), (-1, 2), (1, 2)],
        2: [(0, 0), (-1, -2), (1, -2), (1, -1), (-1, 0), (1, 0), (-1, 1), (-1, 2), (1, 2), (0, 2), (0, -2)],
        3: [(0, 0), (-1, -2), (1, -2), (1, -1), (-1, 0), (1, 0), (1, 1), (-1, 2), (1, 2), (0, 2), (0, -2)],
        4: [(1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (0, 0), (-1, 0), (-1, -1), (-1, -2)],
        5: [(-1, -2), (1, -2), (-1, -1), (-1, 0), (1, 0), (1, 1), (-1, 2), (1, 2), (0, 2), (0, -2), (0, 0)],
        6: [(-1, -2), (1, -2), (-1, -1), (-1, 0), (1, 0), (1, 1), (-1, 2), (1, 2), (0, 2), (0, -2), (0, 0), (-1, 1)],
        7: [(1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (0, -2), (-1, -2)],
        8: [(-1, -2), (1, -2), (-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (-1, 2), (1, 2), (0, 2), (0, -2), (0, 0)],
        9: [(-1, -2), (1, -2), (-1, -1), (1, -1), (-1, 0), (1, 0), (1, 1), (1, 2), (0, -2), (0, 0)]
    }

    left = 0
    top = 0

    for pair in positions:
        pos, colour = pair
        pos = (left+pos[1], top+pos[0])

        string = str(colour + 1)
        if len(string) == 1:
            for (j, i) in digit_map[int(string[0])]:
                draw_point(mat, pos[0]+i, pos[1]+j, text_colour)
        if len(string) == 2:
            for (j, i) in digit_map[int(string[0])]:
                draw_point(mat, pos[0]+i, pos[1]+j-2, text_colour)
            for (j, i) in digit_map[int(string[1])]:
                draw_point(mat, pos[0]+i, pos[1]+j+2, text_colour)

def remove_small_pixels(index_map):
    index_map = np.array(index_map).astype(np.uint8)

    print("Started removing small pixels at: " + str(time.time()))

    index_map = smooth(index_map)
    
    print("Smoothed map at: " + str(time.time()))
    outline_im = outline(index_map)
    print("Outlined image at: " + str(time.time()))
    positions = get_regions(index_map)
    print("Obtained positions at: " + str(time.time()))
    draw_numbers(outline_im, positions, (0, 0, 0))
    print("Drew numbers at: " + str(time.time()))
    return index_map, outline_im
