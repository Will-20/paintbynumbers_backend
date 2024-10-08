
import numpy as np

# These functions return the centroids, they compute k-means
# -----------------------------------------------------------------------------------------

def initialize_centroids(points, k):
    centroids = points.copy().reshape(-1, 3)
    np.random.shuffle(centroids)
    return centroids[:k]

def redmean_distance(points, centroid):
    red = points[:,0]
    green = points[:,1]
    blue = points[:,2]
    dR = red - centroid[0]
    dG = green - centroid[1]
    dB = blue - centroid[2]
    dr = 0.5 * (red + centroid[0])
    dc = (2 + dr/256) * np.square(dR) + 4 * np.square(dG) + (2 + (255-dr)/256) * np.square(dB) 
    return dc

def redmean_closest_centroid(points, centroids):
    distances = np.asarray([redmean_distance(points, c) for c in centroids])
    return np.argmin(distances, axis=0)

def euclid_closest_centroid(points, centroids):
    diff = points - centroids[:, np.newaxis]
    distances = np.einsum('nkd,nkd->nk', diff, diff) 
    return np.argmin(distances, axis=0)

# Try to get new point for empty cluster?
def move_centroids(points, closest, centroids):
    new_centroids = []
    for k in range(centroids.shape[0]):
        cluster = points[closest==k]
        if cluster.shape[0] == 0:
            new_centroids.append(points[np.random.choice(points.shape[0], 1, replace=False)][0])
        else:
            new_centroids.append(np.sqrt((cluster**2).mean(axis=0)))
    return np.asarray(new_centroids)

    # print(points[closest==0].shape)
    # return np.stack([points[closest==k].mean(axis=0) for k in range(centroids.shape[0])])

def get_k_colours(pixels, k, distance='euclidean', num_iter=5):
    centroids = initialize_centroids(pixels, k)
    if distance=='euclidean':
        for i in range(num_iter):
            closest = euclid_closest_centroid(pixels, centroids)
            centroids = move_centroids(pixels, closest, centroids)
        return centroids
    elif distance == 'redmean':
        for i in range(num_iter):
            closest = redmean_closest_centroid(pixels, centroids)
            centroids = move_centroids(pixels, closest, centroids)
        return centroids

# -----------------------------------------------------------------------------------------

def regionise_image(im, num_colours, distance='euclidean'):
    width, height = im.size
    pixels = np.array(im).astype('float16').reshape(width*height, 3)
    k_centroids = np.round(get_k_colours(pixels, num_colours))
    if distance == 'redmean':
        index_map = redmean_closest_centroid(pixels, k_centroids).reshape(height, width)
    else:
        index_map = euclid_closest_centroid(pixels, k_centroids).reshape(height, width)
    return index_map, k_centroids


