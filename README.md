# Cozy Home — патч ресурсов

Resource patch for Cozy Home Refurnished 1.1.20 on Fabric 1.21.1. Fixes missing texture paths in block models.

The recipe was extracted from `netherg-io/blockfield-modpack` at `19cdb35`. Release assets are used by the Blockfield client and server.

Upstream: https://cdn.modrinth.com/data/TNcLBDkY/versions/jJUWZCaQ/Luckys-Cozyhome-Refurnished-1.1.20.jar

The modpack consumes release assets by URL and hash; JARs are not stored in Git. Existing third-party rights are unchanged.

Build with `just setup`, create `files/mods`, then run `just build`. `scripts/toolchain.py` pins Python 3.12.14; the recipe requires standard zlib 1.3.2 at compile time and runtime and rejects other compressors before download/output.

`BUILD-SHA256SUMS` records this canonical local build; `SHA256SUMS` continues to describe the immutable published artifact. Old releases used zlib-ng, whose ZIP bytes differ from standard zlib despite identical uncompressed entries. Do not overwrite a published asset with a rebuild. Local and CI must use the same pinned interpreter and guard; repeat builds in that environment must match `BUILD-SHA256SUMS`. A future published change needs a new game version and normal contract review.

## Описание релиза

Файл `release-notes/<тег>.md` хранится в этом репозитории. Его содержимое используется
как тело GitHub Release и как вложение `release-notes.md`.
[Формат и подготовка](https://github.com/Blockfield/blockfield-client/blob/main/docs/RELEASE-NOTES.md)
описаны в клиентском репозитории; используйте его `scripts/release-notes-tool.py`
из проверенного клона для команд `skeleton` и `check` с параметрами
`--repository Blockfield/cozy-home`, `--version <тег>` и `--kind mod`.
Укажите `backfilled: false`, а в `previous_version` — последнюю опубликованную
версию этой линии.

Публикуйте новый артефакт с контрольными суммами и описанием; старые релизы
не перезаписывайте. После выпуска обновите соответствующие пины сборки.

## Developer checks

Install Python 3.12+, Node.js 22 and Just 1.57.0 on Linux or Windows. Quality tools stay in the project cache.

```sh
just setup
just check
just format
```

`just --list` lists supported build and application commands.

Условия использования: [LICENSE](LICENSE).
