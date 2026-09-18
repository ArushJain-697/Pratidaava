"""
Offline demo — runs the full pipeline on the sample PED-after-36-months case and
pretty-prints the result. No AWS, no API keys, no server. Just:

    pip install pydantic
    python demo.py

Shows: which claims were kept vs STRIPPED (Beat 1), each claim's tier + citation chip,
the promoted lead argument (Beat 2), and the assembled GRO letter.
"""
from __future__ import annotations

from backend.pipeline.run import run_appeal

GREEN = "\033[92m"
YELLOW = "\033[93m"
GREY = "\033[90m"
BOLD = "\033[1m"
RED = "\033[91m"
END = "\033[0m"

TIER_COLOR = {"A": GREEN, "B": YELLOW, "C": GREY, "STRIP": RED}


def main() -> None:
    result = run_appeal()

    print(f"\n{BOLD}=== VERIFIED CLAIMS ==={END}")
    all_claims = result.kept_claims + result.stripped_claims
    for v in all_claims:
        color = TIER_COLOR.get(v.tier.value, "")
        flag = "KEPT " if v.kept else "STRIP"
        print(f"{color}[{flag}] tier {v.tier.value:<5}{END} {v.text}")
        print(f"          {GREY}chip: {v.chip}{END}")

    print(f"\n{BOLD}=== BEAT 1 — the guard ==={END}")
    if result.stripped_claims:
        for v in result.stripped_claims:
            print(f"  {RED}stripped:{END} {v.text}")
    else:
        print("  (nothing stripped)")

    print(f"\n{BOLD}=== BEAT 2 — lead argument ==={END}")
    print(f"  {GREEN}{result.lead_argument}{END}")

    print(f"\n{BOLD}=== FINAL GRO LETTER ==={END}")
    print(result.final_letter)

    # A crude self-check that the thesis invariants hold.
    print(f"{BOLD}=== INVARIANTS ==={END}")
    text_dump = result.model_dump_json()
    assert "%" not in result.final_letter, "no probability in the letter"
    assert "probability" not in text_dump.lower(), "no probability field"
    print(f"  {GREEN}OK{END} no probability anywhere; "
          f"{len(result.kept_claims)} kept, {len(result.stripped_claims)} stripped")


if __name__ == "__main__":
    main()
