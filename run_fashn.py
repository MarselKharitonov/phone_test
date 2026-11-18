"""Manual FASHN experiment; execute only in an explicitly prepared environment."""
import argparse
from pathlib import Path
from stylist.contracts import Category, Frame, TryOnRequest
from stylist.fashn import FashnProvider


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--person", type=Path, required=True)
    parser.add_argument("--garment", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--category", choices=[v.value for v in Category], required=True)
    parser.add_argument("--frame", choices=[v.value for v in Frame], required=True)
    args = parser.parse_args()
    request = TryOnRequest(args.person, args.garment, Category(args.category),
                           Frame(args.frame), args.output)
    print("Experimental output only; it is not QC-approved and must not be served to customers.")
    print(FashnProvider(args.weights).generate(request))


if __name__ == "__main__":
    main()
