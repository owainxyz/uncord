import math
import random
import struct
import unittest

from uncord import voice

HAVE_OPUS = voice.load_opus()


@unittest.skipUnless(HAVE_OPUS, "libopus not found")
class NativeOpusTest(unittest.TestCase):

    def testMatchesDiscordPyDecoder(self):
        from discord import opus

        random.seed(3)
        enc = opus.Encoder()
        packets = []
        for i in range(60):
            pcm = b"".join(struct.pack("<hh", int(8000 * math.sin((i * 960 + k) / 17)), random.randint(-3000, 3000))
                           for k in range(960))
            packets.append(enc.encode(pcm, 960))
        ours, theirs = voice.newDecoder(), opus.Decoder()
        self.assertIsInstance(ours, voice.NativeDecoder)
        for i, p in enumerate(packets):
            if i % 11 == 4:
                self.assertEqual(ours.decode(None, False), theirs.decode(None, fec=False))
            elif i % 13 == 6:
                self.assertEqual(ours.decode(p, True), theirs.decode(p, fec=True))
            else:
                self.assertEqual(ours.decode(p, False), theirs.decode(p, fec=False))

    def testBadInput(self):
        dec = voice.newDecoder()
        with self.assertRaises(ValueError):
            dec.decode(b"\xff\xff\xff", False)
        with self.assertRaises(TypeError):
            dec.decode(None, True)


if __name__ == "__main__":
    unittest.main()
