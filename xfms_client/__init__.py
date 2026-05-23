"""XFMS — Xpansion Framework Model Source. Client library.

Pick the right LLM for your task by hitting the hosted XFMS API
at xfms.xpansion.dev. Inference cost is covered by the hosted
endpoint — you only need a free XFMS access token to use it.

Quick start:

    from xfms_client import XFMSClient

    xfms = XFMSClient()  # reads XFMS_API_KEY from env
    result = xfms.rank("writing a tight editorial under a budget")
    print(result["models"][0]["name"])

See the methodology behind the picks at docs/methodology.md.
Part of the Xpansion Framework — https://xpansion.dev.
"""

from .client import XFMSClient, XFMSError, rank, pick

__version__ = "0.4.0"
__all__ = ["XFMSClient", "XFMSError", "rank", "pick", "__version__"]
