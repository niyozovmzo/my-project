"""Allow running as: python -m dupefind"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
