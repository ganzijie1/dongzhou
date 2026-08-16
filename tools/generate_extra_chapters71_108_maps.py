from __future__ import annotations

try:
    from tools.extra_chapters71_108_data import STAGES
    from tools.generate_chapters82_108_maps import write_map
except ImportError:
    from extra_chapters71_108_data import STAGES
    from generate_chapters82_108_maps import write_map


def main() -> None:
    for index, spec in enumerate(STAGES, start=28):
        write_map(spec, index)
        print(f"generated extra {spec['id']}: {spec['map']} {spec['battle']}")
    print(f"generated {len(STAGES)} split and supplemental battle maps")


if __name__ == "__main__":
    main()
