"""Hello-world example: rank LLMs for a stated purpose.

Run with:
    export XFMS_API_KEY=xfms_live_...
    export OPENROUTER_API_KEY=sk-or-v1-...
    python docs/examples/basic.py
"""

from xfms_client import XFMSClient


def main() -> None:
    with XFMSClient() as xfms:
        result = xfms.rank(
            "writing a tight editorial under a budget",
            top_n=3,
        )

    print(f"Top pick: {result['models'][0]['name']}")
    print()
    print("Inferred weights from your purpose:")
    for w in result.get("inferred_quality_weights", []):
        print(f"  {w['leaf']:32s} {w['weight'] * 100:5.1f}%")
    print()
    if result.get("explanation"):
        print(result["explanation"])


if __name__ == "__main__":
    main()
