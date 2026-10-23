# Prepared GitHub releases

The release kit contains five repository overlays, five component source archives, the complete suite archive, draft notes, recorded public baseline commits and checksums. The KeenTool overlay includes suite/ with the coordinated package; component overlays preserve their normal source paths and existing upstream files/licenses.

Updated sources can be uploaded directly through the GitHub connector as release/stable-20261022 branches and draft pull requests. The connector has no binary release-asset upload operation. Each prepared repository therefore includes a stable-draft workflow: a push to release/stable-* runs validation, assembles archives/checksums on GitHub and creates or refreshes a draft release with GitHub Actions. It explicitly refuses to overwrite a published release and never publishes a draft. Actions must be enabled and repository policy must permit the contents-write workflow token. The kit also includes tools/publish-drafts.sh for a workstation with authenticated GitHub CLI as an alternative. Do not run it if the workflows already created the drafts.

On a workstation with git, gh, tar and sha256sum:

```sh
gh auth status
# Configure your own Git author identity first.
./tools/publish-drafts.sh
```

The script checks checksums, validates that upstream main still matches each recorded baseline, refuses existing release branch/tag names, checks git identity and copies only the prepared overlay. It pushes a release/vX.Y.Z branch, attaches versioned archives/checksums and creates a draft release targeting that branch. Review the source diff and notes, run live router acceptance, then merge and publish each release deliberately. If a baseline has advanced, reconcile changes before rebuilding; do not silently overwrite upstream work.

KeenTool is the coordinated runtime release. Component assets depend on the full KeenTool suite and are not separate bootstrap installers. Preserve attribution and the upstream license for each repository. Do not use a tag already assigned to different code, and do not replace an already downloaded stable asset in place.

The stable changelog uses source commits as baselines because no upstream tags/Releases existed. The GeoIP KP source issue is explicitly included in release notes.

## Remote upgrades

The updater uses published stable release assets, not the review branch or files from main. After review/publishing, keentool --check-updates and keentool --update use the coordinated suite. bootstrap.sh seeds old public/alpha installations once. A draft release is deliberately not offered to router users. Advance RELEASE.json suite version for every published bundle.
