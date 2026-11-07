import hashlib
import random
import unittest

from uncord import _fast as native

#outputs of the old c implementation (_native.c), the rust port has to give exactly the same bytes
GOLDEN = {'sixelRgb': 'dc937b59892604f5', 'sixel40': 'b46d9c38b43c10f7', 'sixelPal': 'b05bdde62df449b8',
          'kitty': 'fdebc750635ee556', 'placeholder': 'c6613eb138d0cd57', 'annexb': '8a1c9dabe2066316',
          'fua': 'bbac49751031ee06', 'rtp': '1975875705cd7dbd', 'ppm': 'eefe2c2ba6511f58'}


def digest(x):
    return hashlib.sha256(repr(x).encode()).hexdigest()[:16]


class NativeTest(unittest.TestCase):

    def testMatchesTheOldC(self):
        random.seed(42)
        px = bytes(random.randint(0, 255) for _ in range(30 * 13 * 3))
        cols = [bytes(random.randint(0, 255) for _ in range(3)) for _ in range(40)]
        px40 = b"".join(random.choice(cols) for _ in range(31 * 17))
        pal = bytes(random.randint(0, 255) for _ in range(3 * 16))
        ip = bytes(random.randint(0, 15) for _ in range(23 * 9))
        data = bytes(random.randint(0, 255) for _ in range(10000))
        annexb = b"\x00\x00\x00\x01\x67abc\x00\x00\x01\x68de\x00\x00\x00\x01\x65" + bytes(range(256)) * 3
        ppm = b"P6\n3 2\n255\n" + bytes(range(18)) + b"P6 1 1 255\n" + b"xyz" + b"P6\n9"
        got = {
            "sixelRgb": digest(native.sixel(px, 30, 13)),
            "sixel40": digest(native.sixel(px40, 31, 17)),
            "sixelPal": digest(native.sixel(ip, 23, 9, pal)),
            "kitty": digest(native.kittyChunks(data, "a=T,f=100", "")),
            "placeholder": digest([native.placeholderRow(r, 0, native.maxCells) for r in range(native.maxCells)]),
            "annexb": digest(native.splitAnnexb(annexb)),
            "fua": digest(native.fuaPayloads(native.splitAnnexb(annexb), 50)),
            "rtp": digest(native.rtpHeader(bytes([0x90, 0xE0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 0, 0, 1, 99]))),
            "ppm": digest(native.ppmFrames(ppm)),
        }
        self.assertEqual(got, GOLDEN)
        self.assertEqual(native.maxCells, 297)

    def testBadInputIsRejectedNotCrashed(self):
        random.seed(9)
        for _ in range(2000):
            junk = bytes(random.randint(0, 255) for _ in range(random.randint(0, 80)))
            native.splitAnnexb(junk)
            native.rtpHeader(junk)
            native.ppmFrames(junk)
            native.hasPixels(junk)
        with self.assertRaises(ValueError):
            native.sixel(b"\x00" * 5, 2, 2)
        with self.assertRaises(ValueError):
            native.sixel(b"\x09", 1, 1, b"\x00\x00\x00")
        with self.assertRaises(ValueError):
            native.placeholderRow(0, 0, native.maxCells + 1)
        distinct = b"".join(bytes((i % 256, i // 256, 7)) for i in range(257))
        self.assertIsNone(native.sixel(distinct, 257, 1))


if __name__ == "__main__":
    unittest.main()
