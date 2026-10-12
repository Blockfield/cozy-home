#!/usr/bin/env python3
"""Пересобрать files/mods/*-bf1.jar из апстримного jar-а с Modrinth.

Cozy Home: в inset_flat_11/13 (подмодели воды в раковинах) и в item/falling_liquid
битые ссылки -- texture воды переехала в block/liquid/, а block/falling_liquid не
существует (нужен stream_water_falling). Проявлялось как magenta-вода в mud_sink
на картах и "Unable to load model" в клиентском логе.

replace: точечные замены текста внутри записей jar (кортежи "запись, старое, новое").
Если замена ни разу не сработала, сборка падает.

Запуск: just build
"""

import hashlib
import io
import sys
import urllib.request
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

JARS = [
    {
        "upstream_name": "Luckys-Cozyhome-Refurnished-1.1.20.jar",
        "url": "https://cdn.modrinth.com/data/TNcLBDkY/versions/jJUWZCaQ/Luckys-Cozyhome-Refurnished-1.1.20.jar",
        "sha512": "8964b597c1a400970b834a1a4058df9332a687a7452ffc889ba8fe3cb35347d8512011d3679a24e7d1fa0f5f9904de3e1f7710b95f2e1fe6cb5b43b0c9f12847",
        "out": "files/mods/Luckys-Cozyhome-Refurnished-1.1.20-bf1.jar",
        "replace": [
            (
                "assets/cozyhome/models/block/flat/inset_flat_11.json",
                "cozyhome:block/inset_water_still",
                "cozyhome:block/liquid/inset_water_still",
            ),
            (
                "assets/cozyhome/models/block/flat/inset_flat_13.json",
                "cozyhome:block/inset_water_still",
                "cozyhome:block/liquid/inset_water_still",
            ),
            (
                "assets/cozyhome/models/item/falling_liquid.json",
                "cozyhome:block/falling_liquid",
                "cozyhome:block/stream_water_falling",
            ),
        ],
    }
]


def get_bytes(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Blockfield-CI/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def sha512(data):
    return hashlib.sha512(data).hexdigest()


def apply_replacements(name, text, spec):
    hits = 0
    for old, new in spec:
        count = text.count(old)
        if count == 0:
            sys.exit(f"{name}: замена не нашла {old!r} -- паттерн устарел?")
        text = text.replace(old, new)
        hits += count
    return text, hits


def main():
    if (zlib.ZLIB_VERSION, zlib.ZLIB_RUNTIME_VERSION) != ("1.3.2", "1.3.2"):
        sys.exit(
            f"Expected zlib 1.3.2 (standard), got {zlib.ZLIB_VERSION}/{zlib.ZLIB_RUNTIME_VERSION}; run just build"
        )
    for spec in JARS:
        out_path = ROOT / spec["out"]
        local = ROOT / "files" / "mods" / spec["upstream_name"]
        if local.is_file():
            data = local.read_bytes()
        else:
            print(f"скачиваю {spec['upstream_name']}")
            data = get_bytes(spec["url"])
        actual = sha512(data)
        if actual != spec["sha512"]:
            sys.exit(f"Апстрим изменился: {spec['upstream_name']} sha512 {actual}")

        source = zipfile.ZipFile(io.BytesIO(data))
        replacements = dict.fromkeys(spec["replace"], 0)
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as target:
            for info in source.infolist():
                name = info.filename
                payload = source.read(name)
                for entry, old, new in spec["replace"]:
                    if entry == name:
                        text, hits = apply_replacements(
                            name, payload.decode("utf-8"), [(old, new)]
                        )
                        payload = text.encode("utf-8")
                        replacements[(entry, old, new)] = hits
                target.writestr(info, payload)
        for (entry, old, new), hits in replacements.items():
            if hits == 0:
                sys.exit(f"{entry}: запись для замены не найдена")
            print(f"  ~ {entry}: {old.split('/')[-1]} -> {new} (x{hits})")
        print(
            f"{out_path.relative_to(ROOT)} <- {spec['upstream_name']} (sha512 {sha512(out_path.read_bytes())})"
        )


if __name__ == "__main__":
    main()
