#!/usr/local/bin/python3
import os
import sys
import pickle
from time import time

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.path import Path
from scipy import interpolate
from scipy.spatial import Delaunay

from more_cores import *

num_frames = int(sys.argv[1])
num_servers = int(sys.argv[2])
num_cores = 4 if len(sys.argv) < 4 else int(sys.argv[3])
print('==================================')
print(num_frames, num_servers, num_cores)
print('==================================')

# Check hivemind.eecs.berkeley.edu to see which machines are currently online
available_hives = [2, 3, 18, 19, 20, 24][:num_servers]
hive = Cores(
    [
        make_server_dict('hive{}.cs.berkeley.edu'.format(i), 'cs199-dlq', dfs=0, cores=num_cores) for i in available_hives
    ],
    make_requirements(['matplotlib', 'scipy', 'numpy'])
)


@parallel_for(hive)
def process_image_n(num_images: int, image_0: np.array, image_1: np.array,
                    points_0: np.array, point_change: np.array,
                    triangulation_indices: np.array, triangulation_0: np.array,
                    triangulation_1: np.array, n):

    def get_interpolation_function(source_image):
        x_axis, y_axis = np.arange(source_image.shape[1]), np.arange(source_image.shape[0])
        channel_functions = [
            interpolate.interp2d(x_axis, y_axis, source_image[:, :, d]) for d in range(source_image.shape[2])
        ]

        def interpolation_function(point):
            return np.array([
                channel_function(point[1], point[0]) for channel_function in channel_functions
            ]).T

        return interpolation_function

    print("Computing frame {}".format(n))
    interpolate_0, interpolate_1 = get_interpolation_function(image_0), get_interpolation_function(image_1)
    warp_fraction = (n + 1) / (num_images + 1)
    points = points_0 + point_change * warp_fraction
    triangulation = points[triangulation_indices]

    num_triangles = triangulation.shape[0]

    image = np.zeros_like(image_0)
    # Compute transforms for every triangle
    transforms_0 = [None] * num_triangles
    transforms_1 = [None] * num_triangles
    for triangle_index in range(num_triangles):
        transforms_0[triangle_index] = compute_transformation(triangulation[triangle_index],
                                                              triangulation_0[triangle_index])
        transforms_1[triangle_index] = compute_transformation(triangulation[triangle_index],
                                                              triangulation_1[triangle_index])
    # Iterate through every triangle in the new image
    for triangle_index in range(num_triangles):
        vertices = triangulation[triangle_index]
        r_min, c_min = np.min(vertices, axis=0).astype(int)
        r_max, c_max = np.max(vertices, axis=0).astype(int)
        #  Check every point in the bounding box
        for r in range(r_min, r_max+1):
            for c in range(c_min, c_max+1):
                if not Path(vertices).contains_point((r, c)):
                    continue
                # Transform points
                point_0 = transform_point((r, c), transforms_0[triangle_index])
                point_1 = transform_point((r, c), transforms_1[triangle_index])
                # Interpolate
                pixel_0 = interpolate_0(point_0)
                pixel_1 = interpolate_1(point_1)
                # Combine
                image[r, c] = pixel_0 * (1 - warp_fraction) + pixel_1 * warp_fraction

    return image


def load_image(image_name):
    return plt.imread(image_name + '.jpg') / 255


def get_clicks(images, num_features):
    """Return a list of point sets corresponding to a list of images."""
    num_images = len(images)
    plt.imshow(np.hstack(images))
    clicks = np.array(plt.ginput(n=num_features * num_images, timeout=0, show_clicks=True))
    height, width = images[0].shape[:2]
    for i in range(len(clicks)):
        clicks[i][0] = clicks[i][0] - width * (i % num_images)
        clicks[i][0], clicks[i][1] = clicks[i][1], clicks[i][0]
    plt.close()
    return [
        clicks[i::num_images] for i in range(num_images)
    ]


def get_midpoints(points_0, points_1):
    return np.array([
        ((p_0[0] + p_1[0]) / 2, (p_0[1] + p_1[1]) / 2) for p_0, p_1 in zip(points_0, points_1)
    ])


def save_points(image_name_0, image_name_1, num_features):
    image_0, image_1 = load_image(image_name_0), load_image(image_name_1)
    height, width = image_0.shape[:2]
    corners = np.array([[0, 0], [height - 1, 0], [0, width - 1], [height - 1, width - 1]])
    clicks = get_clicks((image_0, image_1), num_features)
    points = np.vstack((clicks[0], corners)), np.vstack((clicks[1], corners))
    with open(image_name_0, 'wb') as fp:
        pickle.dump(points[0], fp)
    with open(image_name_1, 'wb') as fp:
        pickle.dump(points[1], fp)


def load_points(image_name):
    with open(image_name, 'rb') as fp:
        points = pickle.load(fp)
    return np.array(points)


def compute_transformation(triangle_0, triangle_1):
    triangle_0_mat = np.vstack((triangle_0.T, np.ones((1, 3))))
    triangle_1_mat = np.vstack((triangle_1.T, np.ones((1, 3))))
    return triangle_1_mat @ np.linalg.inv(triangle_0_mat)


def transform_point(point, transformation):
    return (transformation @ [point[0], point[1], 1])[:-1]


def get_triangulation_indices(points_0, points_1):
    midpoints = get_midpoints(points_0, points_1)
    return Delaunay(midpoints).simplices


def morph(image_name_0, image_name_1, num_images, image_range):
    image_0, image_1 = load_image(image_name_0), load_image(image_name_1)
    points_0, points_1 = load_points(image_name_0), load_points(image_name_1)
    assert image_0.shape == image_1.shape
    assert points_0.shape == points_1.shape

    triangulation_indices = get_triangulation_indices(points_0, points_1)
    triangulation_0, triangulation_1 = points_0[triangulation_indices], points_1[triangulation_indices]
    point_change = points_1 - points_0

    ts = time()
    frames = process_image_n(
            num_images, image_0, image_1, points_0, point_change,
            triangulation_indices, triangulation_0, triangulation_1,
            Iterable(list(range(image_range[0], image_range[1] + 1)))
    )
    t = time() - ts
    with open('out.txt', 'w+') as fp:
        fp.writelines(['{} {} {}'.format(num_frames, num_servers, num_images)])
    print('Time:', t / 60)
    return frames


def process_images(image_name_0, image_name_1, num_frames, num_points=None, image_range=None):
    if image_range is None:
        image_range = (1, num_frames)
    directory_name = '{}_{}'.format(image_name_0, image_name_1)
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    if num_points is not None:
        save_points(image_name_0, image_name_1, num_points)
    images = morph(image_name_0, image_name_1, num_frames, image_range)
    for f in range(image_range[0], image_range[1] + 1):
        plt.imsave('{}/{:02}.jpg'.format(directory_name, f), images[f - image_range[0]])


if __name__ == '__main__':
    process_images('blue_animated', 'plushie', num_frames)
