import wave
import struct
from scipy.fftpack import dct, idct

from ..helpers import band_filter


class WaveHandler(object):
    """Handle wave file read and write."""
    def __init__(self, fn, block_size, mode='r'):
        self._f = wave.open(fn, mode)
        self._mode = mode
        self._block_size = block_size

    def __call__(self, *args, **kwargs):
        sampwidth, num_channel = self._f.getsampwidth(), self._f.getnchannels()
        if sampwidth == 1:
            # unsigned 8-bit PCM
            struct_str = '<B'
            high, mean = 2.0 ** 7, 1
        elif sampwidth == 2:
            # signed 16-bit PCM (how to tell when it's big-endian?)
            struct_str = '<h'
            high, mean = 2.0 ** 15, 0
        else:
            raise NotImplementedError('sample width is not 8 or 16 bits. (got {})'.format(sampwidth * 8))

        if self._mode == 'r':
            return self._read_func(sampwidth, num_channel, struct_str, high, mean)
        elif self._mode == 'w':
            self._write_func(sampwidth, num_channel, struct_str, high, mean, *args)

    def _read_func(self, sampwidth, num_channel, ss, high, mean):
        def _data_generator(s, a, m, p, l, e, struct_str):
            padding = []
            num_frames = s.getnframes()
            while num_frames > 0:
                data_bytes = s.readframes(a)
                num_frames -= a
                if num_frames < 0:
                    padding = [0] * (-num_frames)
                frames = map(''.join, (zip(*[iter(data_bytes)] * m)))
                audio_data = [frames[i::p] for i in xrange(p)]
                data = [[struct.unpack(struct_str, y)[0] / l - e for y in x] + padding for x in audio_data]
                yield dct(data, norm='ortho')
            s.close()
        return _data_generator(self._f, self._block_size, sampwidth, num_channel, high, mean, ss)

    def _write_func(self, sampwidth, num_channel, ss, high, mean, *args):
        # for writing, set params first before calling
        for arg in args:
            if len(arg) != num_channel:
                raise ValueError('input mismatches number of channels. (got {})'.format(len(arg)))
            data_bytes = []
            for i in xrange(num_channel):
                recov_data = idct(arg[i], norm='ortho')
                data_bytes.append([struct.pack(ss, high * (band_filter(x, -1, 1) + mean)) for x in recov_data])
            self._f.writeframes(''.join([val for tup in zip(*data_bytes) for val in tup]))

    def params(self, *args):
        if self._mode == 'r':
            return self._f.getparams()
        elif self._mode == 'w':
            self._f.setparams(args)

    def close(self):
        if self._mode == 'r':
            raise ValueError('cannot manually close when in read mode.')
        self._f.close()

    @property
    def mode(self):
        return self._mode
