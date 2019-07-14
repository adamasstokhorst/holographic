import numpy
from PIL import Image

from ..helpers import band_filter


class ImageHandler(object):
    """Handle image file read and write."""
    def __init__(self, fn, block_size, mode='r', color_mode='L'):
        self._mode = mode.lower()
        self._block_size = block_size
        self._block_width = int((block_size + 1)**0.5)  # dirty way to check for squareness
        self._average = None
        self._x, self._y = 0, 0
        if self._block_width**2 != self._block_size:
            raise ValueError('block_size must be a perfect square. (got {})'.format(block_size))
        if mode == 'r':
            self._f = Image.open(fn).convert(color_mode)
            self._fn = fn
            self._height = self._f.width
            self._width = self._f.height
            self._num_bands = len(color_mode)  # hack
        elif self._mode == 'w':
            self._f = Image.new(mode=mode, size=(1, 1))
            self._fn = fn
            self._height = None
            self._width = None
            self._num_bands = len(color_mode)  # hack

    def __call__(self, *args, **kwargs):
        right_pad = self._block_width - self._width % self._block_width
        right_pad -= self._block_width if right_pad == self._block_width else 0
        bottom_pad = self._block_width - self._height % self._block_width
        bottom_pad -= self._block_width if bottom_pad == self._block_width else 0
        lr_blocks = (self._width + right_pad) / self._block_width
        ud_blocks = (self._height + bottom_pad) / self._block_width
        
        if self._mode == 'r':
            pixels = [numpy.array(list(self._f.getdata(band=x))) for x in xrange(self._num_bands)]
            for p in pixels:
                p.shape = (self._height, self._width)
                p = numpy.pad(p, ((0, bottom_pad), (0, right_pad)), 'edge') / 128.0 - 1
            
            self._average = numpy.zeros((1, self._block_size))
            for i, j in [(x, y) for x in xrange(lr_blocks) for y in xrange(ud_blocks)]:
                for p in pixels:
                    self._average += p[j*self._block_width:(j+1)*self._block_width, i*self._block_width:(i+1)*self._block_width].flatten()
            self._average /= lr_blocks * ud_blocks
            for i, j in [(x, y) for x in xrange(lr_blocks) for y in xrange(ud_blocks)]:
                yield [list(p[j*self._block_width:(j+1)*self._block_width, i*self._block_width:(i+1)*self._block_width].flatten()) for p in pixels]
            self._f.close()
        elif self._mode == 'w':
            # for writing, set params first before calling
            pixels = [band_filter(128*(y + 1), 0, 255) for x in args for y in x]
            pixels = numpy.array(pixels, dtype='uint8')
            patch_size = self._block_width, self._block_width, self._num_bands
            if self._y == ud_blocks - 1:
                patch_size = self._block_width - bottom_pad, patch_size[1], patch_size[2]
            if self._x == lr_blocks - 1:
                patch_size = patch_size[0], self._block_width - right_pad, patch_size[2]
            pixels.shape = patch_size
            patch = Image.fromarray(pixels)
            self._f.paste(patch, (self._x*self._block_width, self._y*self._block_width))
            patch.close()
            self._x += 1
            if self._x >= lr_blocks:
                self._x = 0
                self._y += 1

    def params(self, *args):
        if self._mode == 'r':
            return self._height, self._width
        elif self._mode == 'w':
            self._height = args[0]
            self._width = args[1]
            self._f = self._f.resize(args)

    def close(self):
        if self._mode == 'r':
            raise ValueError('cannot manually close when in read mode.')
        self._f.save(self._fn)
        self._f.close()

    @property
    def mode(self):
        return self._mode

    @property
    def average(self):
        return self._average
