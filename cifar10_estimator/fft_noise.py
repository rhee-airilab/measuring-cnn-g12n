# coding: utf-8
from __future__ import print_function,division,absolute_import

import numpy as np

def mask_radial(shape, r, inv=False, center=True):
    h, w = shape

    mask = np.zeros(shape)

    if center:
        cx = w//2
        cy = h//2
    else:
        cx = 0
        cy = 0 # h-1

    for x in range(w):
        rx = abs(cx - x)
        ry = int(np.sqrt(r ** 2 - rx ** 2)) if rx < r else 0
        y1 = max(0, cy - ry)
        y2 = min(h, cy + ry)
        mask[y1:y2,x] = 1.0
            
    if inv:
        mask = 1 - mask

    return mask


def mask_random(shape, p, seed=80208700):
    h, w = shape
    np.random.seed(seed)
    mask = (np.random.uniform(size=shape) > p).astype(int)
    return mask


def apply_mask(image, mask):
    orig_dt = None
    if np.amax(image) > 1.1:
        orig_dt = image.dtype
        image = image / 255.0
    fft2 = np.fft.fftshift(np.fft.fft2(image[:,:]))
    fft2 *= mask
    # fix imaginary values
    image2 = np.real(np.fft.ifft2(np.fft.ifftshift(fft2[:,:])))
    # fix range
    image2 = np.minimum(1.0,np.maximum(0.0,image2))
    # fix dtype
    if orig_dt is not None:
        image2 = (image2 * 255).astype(orig_dt)
    return image2

