# Blockfield — cozy-home

Private patch recipe and pinned release artifacts. Imported from `netherg-io/blockfield-modpack` at `19cdb35`.

Upstream: https://cdn.modrinth.com/data/TNcLBDkY/versions/jJUWZCaQ/Luckys-Cozyhome-Refurnished-1.1.20.jar

The modpack consumes release assets by URL and hash; JARs are not stored in Git. Existing third-party rights are unchanged.

Build with `just setup`, create `files/mods`, then run `just build`. `scripts/toolchain.py` pins Python 3.12.14; the recipe requires standard zlib 1.3.2 at compile time and runtime and rejects other compressors before download/output. ImageMagick 7 is needed only for icon patches.

`BUILD-SHA256SUMS` records this canonical local build; `SHA256SUMS` continues to describe the immutable published artifact. Old releases used zlib-ng, whose ZIP bytes differ from standard zlib despite identical uncompressed entries. Do not overwrite a published asset with a rebuild. Local and CI must use the same pinned interpreter and guard; repeat builds in that environment must match `BUILD-SHA256SUMS`. A future published change needs a new game version and normal contract review.

## Описание релиза (release-notes.md)

Каждый новый релиз публикуется с описанием в едином формате Blockfield: тело релиза и asset `release-notes.md` — один и тот же файл `release-notes/<тег>.md`, закоммиченный в этот репозиторий. Инструмент проверки общий, из `Blockfield/blockfield-client`:

```sh
mkdir -p release-notes rn
gh api repos/Blockfield/blockfield-client/contents/scripts/release-notes-tool.py \
  -H 'Accept: application/vnd.github.raw' > rn/release-notes-tool.py
just python rn/release-notes-tool.py skeleton --repository Blockfield/cozy-home --version <тег> \
  --previous-version <прошлый тег> --kind mod --date YYYY-MM-DD > release-notes/<тег>.md
# заполните разделы по коммитам и изменениям рецепта; чего не знаете — отметьте в «Источниках»
just python rn/release-notes-tool.py check release-notes/<тег>.md \
  --repository Blockfield/cozy-home --version <тег> --kind mod
cp release-notes/<тег>.md rn/release-notes.md
gh release create <тег> <артефакты> SHA256SUMS rn/release-notes.md \
  --notes-file rn/release-notes.md --repo Blockfield/cozy-home
```

Если `check` выводит ошибки, релиз не публикуйте. После выпуска обновите пин в клиенте/сервере; их релизные описания подтянут этот файл в раздел «Обновлённые компоненты».

## Developer checks

Install Python 3.12+, Node.js 22 and Just 1.57.0 on Linux or Windows. Quality tools stay in the project cache.

```sh
just setup
just check
just format
```

`just --list` lists supported build and application commands.
