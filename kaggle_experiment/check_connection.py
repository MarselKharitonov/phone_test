"""Read-only Kaggle check. Does not create or start a notebook."""
import sys


def main():
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        notebooks = api.kernels_list(mine=True, page_size=5)
        print(f"Connection successful. Up to {len(notebooks)} notebooks found.")
    except Exception as exc:
        # Avoid printing provider responses that might contain credentials.
        print(f"Connection failed ({type(exc).__name__}). Check local Kaggle setup.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
