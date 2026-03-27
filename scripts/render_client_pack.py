#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from render_customer_profile_card import render as render_profile_card
from render_allocation_path import render as render_allocation_path


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description='Render a private-banking client pack (profile card + allocation path).')
    parser.add_argument('--input', required=True, help='Path to combined JSON input')
    parser.add_argument('--output-dir', required=True, help='Directory for outputs')
    parser.add_argument('--prefix', default='client_pack', help='Filename prefix')
    parser.add_argument('--skip-card', action='store_true')
    parser.add_argument('--skip-path', action='store_true')
    args = parser.parse_args()

    payload = load_json(Path(args.input))
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    created = []

    if not args.skip_card and payload.get('profile_card'):
        img = render_profile_card(payload['profile_card'])
        png = outdir / f'{args.prefix}_profile_card.png'
        pdf = outdir / f'{args.prefix}_profile_card.pdf'
        img.save(png)
        img.convert('RGB').save(pdf, 'PDF', resolution=150.0)
        created.extend([str(png), str(pdf)])

    if not args.skip_path and payload.get('allocation_path'):
        img = render_allocation_path(payload['allocation_path'])
        png = outdir / f'{args.prefix}_allocation_path.png'
        pdf = outdir / f'{args.prefix}_allocation_path.pdf'
        img.save(png)
        img.convert('RGB').save(pdf, 'PDF', resolution=150.0)
        created.extend([str(png), str(pdf)])

    print(json.dumps({'ok': True, 'created': created}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
