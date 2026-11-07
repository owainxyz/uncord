import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uncord import fmt

PLAIN = ["lol yeah", "im on my way rn", "did you see that", "nah that's mad", "ok", "gg",
         "what time are we playing tonight", "brb"]
RICH = ["**bold** and *it* with `code`", "check https://github.com/owainxyz/uncord out",
        "<@123> look at this ||spoiler||", "> quote\nreply here", "- one\n- two\n- three",
        "```py\nprint('hi')\nfor i in range(3):\n    pass\n```", "[click](https://example.com) <t:1700000000:R>"]


def main(n: int = 20000) -> None:
    random.seed(1)
    corpus = [random.choice(PLAIN) if random.random() < .75 else random.choice(RICH) for _ in range(n)]
    ctx = fmt.MdContext(1)
    best = float("inf")
    for _ in range(3):
        start = time.perf_counter()
        for text in corpus:
            fmt.markdown(text, ctx)
        best = min(best, time.perf_counter() - start)
    print(f"markdown: {best * 1e6 / n:.1f} µs per message ({n} messages, 75% plain)")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20000)
