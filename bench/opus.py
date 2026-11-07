import math
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from discord import opus

from uncord import _dsp, voice


def main(n: int = 3000) -> None:
    if not voice.load_opus():
        print("libopus not found")
        return
    _dsp.opusLoad(opus._lib._name)
    enc = opus.Encoder()
    pcm = b"".join(struct.pack("<hh", int(8000 * math.sin(i / 20)), int(6000 * math.sin(i / 31))) for i in range(960))
    packets = [enc.encode(pcm, 960) for _ in range(n)]
    for name, make, dec in (
        ("ctypes (discord.py)", opus.Decoder, lambda d, p: d.decode(p, fec=False)),
        ("native (_dsp)", _dsp.opusDecoder, lambda d, p: _dsp.opusDecode(d, p, False)),
    ):
        best = float("inf")
        for _ in range(3):
            d = make()
            start = time.perf_counter()
            for p in packets:
                dec(d, p)
            best = min(best, time.perf_counter() - start)
        print(f"opus decode, {name}: {best * 1e6 / n:.1f} µs per 20 ms frame")


if __name__ == "__main__":
    main()
