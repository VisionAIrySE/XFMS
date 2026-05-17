"""XFMS — Xpansion Framework Model Source. Client library.

Pick the right LLM for your task by hitting the hosted XFMS API
at xfms.vercel.app. BYOK — you supply your own OpenRouter key so
your inference cost stays with you.

Quick start:

    from xfms_client import XFMSClient

    xfms = XFMSClient()  # reads XFMS_API_KEY + OPENROUTER_API_KEY from env
    result = xfms.rank("writing a tight editorial under a budget")
    print(result["models"][0]["name"])

See the methodology behind the picks at docs/methodology.md.
Part of the Xpansion Framework — https://xpansion.dev.
"""

from .client import XFMSClient, XFMSError, rank, pick

__version__ = "0.3.0"
__all__ = ["XFMSClient", "XFMSError", "rank", "pick", "__version__"]
