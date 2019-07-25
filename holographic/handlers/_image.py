import numpy
from PIL import Image

from ..helpers import band_filter


class ImageHandler(object):
    """Handle image file read and write."""
    def __init__(self, fn, block_size, mode='r', color_mode='L'):
        self._mode = mode.lower()
        self._color_mode = color_mode
        self._block_size = block_size
        self._block_width = int((block_size + 1)**0.5)  # dirty way to check for squareness
        self._average = None
        self._x, self._y = 0, 0
        self._bottom_pad, self._right_pad = None, None
        self._lr_blocks, self._ud_blocks = None, None
        if self._block_width**2 != self._block_size:
            raise ValueError('block_size must be a perfect square. (got {})'.format(block_size))
        if mode == 'r':
            self._f = Image.open(fn).convert(color_mode)
            self._fn = fn
            self._height = self._f.width
            self._width = self._f.height
            self._num_bands = len(color_mode)  # hack
        elif self._mode == 'w':
            self._f = Image.new(mode=color_mode, size=(1, 1))
            self._fn = fn
            self._height = None
            self._width = None
            self._num_bands = len(color_mode)  # hack

    def __call__(self, *args, **kwargs):
        if self._lr_blocks is None:
            right_pad = self._block_width - self._width % self._block_width
            right_pad -= self._block_width if right_pad == self._block_width else 0
            bottom_pad = self._block_width - self._height % self._block_width
            bottom_pad -= self._block_width if bottom_pad == self._block_width else 0
            lr_blocks = (self._width + right_pad) / self._block_width
            ud_blocks = (self._height + bottom_pad) / self._block_width
            self._lr_blocks = lr_blocks
            self._ud_blocks = ud_blocks
            self._bottom_pad = bottom_pad
            self._right_pad = right_pad

        if self._mode == 'r':
            return self._read_func()
        else:
            self._write_func(*args)

    def _read_func(self):
        lr_blocks = self._lr_blocks
        ud_blocks = self._ud_blocks
        bottom_pad = self._bottom_pad
        right_pad = self._right_pad

        pixels = [numpy.array(list(self._f.getdata(band=x))) for x in xrange(self._num_bands)]
        for i, p in enumerate(pixels):
            p.shape = self._width, self._height
            pixels[i] = numpy.pad(p, ((0, right_pad), (0, bottom_pad)), 'edge') / 128.0 - 1

        self._average = numpy.zeros((1, self._block_size))
        for i, j in [(x, y) for x in xrange(ud_blocks) for y in xrange(lr_blocks)]:
            for p in pixels:
                self._average += p[j*self._block_width:(j+1)*self._block_width, i*self._block_width:(i+1)*self._block_width].flatten()
        self._average /= lr_blocks * ud_blocks
        for i, j in [(x, y) for x in xrange(ud_blocks) for y in xrange(lr_blocks)]:
            yield [list(p[j*self._block_width:(j+1)*self._block_width, i*self._block_width:(i+1)*self._block_width].flatten()) for p in pixels]
        self._f.close()

    def _write_func(self, *args):
        lr_blocks = self._lr_blocks
        ud_blocks = self._ud_blocks

        # provide multiple arguments to write all of them in one go
        for arg in args:
            # for writing, set params first before calling
            pixels = reduce(lambda a, b: a + b, zip(*arg))
            pixels = [band_filter(128*(x + 1), 0, 255) for x in pixels]
            pixels = numpy.array(pixels, dtype='uint8')

            if self._num_bands == 1:
                pixels.shape = self._block_width, self._block_width
            else:
                pixels.shape = self._block_width, self._block_width, self._num_bands

            patch = Image.fromarray(pixels)
            self._f.paste(patch, (self._x*self._block_width, self._y*self._block_width))
            patch.close()
            self._y += 1
            if self._y >= ud_blocks:
                self._y = 0
                self._x += 1

    def params(self, *args):
        if self._mode == 'r':
            return self._height, self._width
        elif self._mode == 'w':
            self._width = args[0]
            self._height = args[1]
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
    def color_mode(self):
        return self._color_mode

    @property
    def average(self):
        return self._average
