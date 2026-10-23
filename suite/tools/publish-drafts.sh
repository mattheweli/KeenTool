#!/usr/bin/env bash
# Create reviewable release branches and GitHub drafts; never merge or publish.
set -Eeuo pipefail
kit=$(cd "$(dirname "$0")/.." && pwd)
for tool in gh git python3 sha256sum;do command -v "$tool" >/dev/null || { echo "Missing: $tool" >&2;exit 1; };done
[ -f "$kit/release-plan.json" ] || { echo 'Run the copy of this script inside the generated release kit' >&2;exit 1; }
(cd "$kit" && sha256sum -c CHECKSUMS.sha256) >/dev/null
gh auth status
git var GIT_AUTHOR_IDENT >/dev/null || { echo 'Configure your Git author name/email first' >&2;exit 1; }
work=$(mktemp -d);trap 'rm -rf "$work"' EXIT
python3 - "$kit/release-plan.json" > "$work/plan.tsv" <<'PY'
import json,sys
for r in json.load(open(sys.argv[1])):print(r['repository'],r['tag'],r['baseline_commit'],r['version'],sep='\t')
PY
# Complete read-only baseline/name preflight for all repositories before the first push.
while IFS=$'\t' read -r repo tag baseline version;do
 actual=$(git ls-remote "https://github.com/$repo.git" refs/heads/main | cut -f1)
 [ "$actual" = "$baseline" ] || { echo "main advanced in $repo; reconcile before releasing" >&2;exit 1; }
 existing=$(git ls-remote "https://github.com/$repo.git" "refs/tags/$tag" "refs/heads/release/$tag")
 [ -z "$existing" ] || { echo "Tag or release branch already exists: $repo $tag" >&2;exit 1; }
done < "$work/plan.tsv"
while IFS=$'\t' read -r repo tag baseline version;do
 name=${repo#*/};checkout="$work/$name"
 git clone --quiet "https://github.com/$repo.git" "$checkout"
 git -C "$checkout" checkout --quiet -b "release/$tag" "$baseline"
 cp -a "$kit/repositories/$name/." "$checkout/"
 git -C "$checkout" add --all
 git -C "$checkout" commit -m "Prepare $name $version stable release"
 git -C "$checkout" -c credential.helper= -c 'credential.helper=!gh auth git-credential' push origin "release/$tag"
 files=("$kit/assets/$name-$version-sources.tar.gz" "$kit/assets/$name-$version-sources.tar.gz.sha256")
 if [ "$name" = KeenTool ];then files+=("$kit/assets/keentool-$version.tar.gz" "$kit/assets/keentool-$version.tar.gz.sha256" "$kit/assets/keentool-$version-manifest.json" "$kit/assets/keentool-$version-manifest.json.sha256");fi
 gh release create "$tag" "${files[@]}" --repo "$repo" --draft --target "release/$tag" --title "$name $version" --notes-file "$kit/notes/$name.md"
done < "$work/plan.tsv"
echo 'Draft releases created. Review diffs, run live acceptance, then merge/publish deliberately.'
