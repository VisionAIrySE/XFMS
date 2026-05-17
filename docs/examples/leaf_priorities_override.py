"""Example: override the system's per-leaf weight inference.

When you know which quality dimension matters most, say so — your
stated priority always wins over the LLM's inference.
"""

from xfms_client import XFMSClient


def main() -> None:
    with XFMSClient() as xfms:
        # The LLM might infer this is a "code" task and weight
        # structured_output_reliability + instruction_following.
        # We're saying: no — for THIS specific code task, factuality
        # matters more (e.g., refactoring a security-sensitive
        # parser where one wrong fix is a CVE).
        result = xfms.rank(
            "refactoring our authentication middleware",
            leaf_priorities={
                "factuality": 1.0,
                "structured_output_reliability": 0.5,
            },
        )

    print(f"Top pick: {result['models'][0]['name']}")
    print(f"Score:    {result['models'][0]['total_score']:.3f}")


if __name__ == "__main__":
    main()
