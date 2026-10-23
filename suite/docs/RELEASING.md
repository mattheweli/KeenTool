# Prepared GitHub releases

A release kit contains changed repository overlays and source archives, the complete suite archive, release notes, recorded public baseline commits and checksums. The 2.0.1 patch changes KeenTool and keenetic-firewall only; the other three repository versions remain unchanged. The KeenTool overlay includes suite/ with the coordinated package; component overlays preserve their normal source paths and existing upstream files/licenses.

Updated sources can be uploaded directly through the GitHub connector as release/stable-* branches and draft pull requests. The connector has no binary release-asset upload operation. Each prepared repository therefore includes a stable-draft workflow: a push to release/stable-* runs validation, assembles archives/checksums on GitHub and creates or refreshes a draft release with GitHub Actions. It explicitly refuses to overwrite a published release and never publishes a draft. Actions must be enabled and repository policy must permit the contents-write workflow token. The kit also includes tools/publish-drafts.sh for a workstation with authenticated GitHub CLI as an alternative. Do not run it if the workflows already created the drafts.

On a workstation with git, gh, tar and sha256sum:

```sh
gh auth status
# Configure your own Git author identity first.
./tools/publish-drafts.sh
```

The script checks checksums, validates that upstream main still matches each recorded baseline, refuses existing release branch/tag names, checks git identity and copies only the prepared overlay. It pushes a release/vX.Y.Z branch, attaches versioned archives/checksums and creates a draft release targeting that branch. Review the source diff and notes, run live router acceptance, then merge and publish each release deliberately. If a baseline has advanced, reconcile changes before rebuilding; do not silently overwrite upstream work.

KeenTool is the coordinated runtime release. Component assets depend on the full KeenTool suite and are not separate bootstrap installers. Preserve attribution and the upstream license for each repository. Do not use a tag already assigned to different code, and do not replace an already downloaded stable asset in place.

The patch changelog is relative to the preceding published stable tags. First-stable source baselines and alpha history are archived separately. The GeoIP KP source issue is explicitly included in release notes.

## Remote upgrades

The updater uses published stable release assets, not the review branch or files from main. After review/publishing, keentool --check-updates and keentool --update use the coordinated suite. The new manager embeds the bootstrap before loading shared libraries, allowing the historical public Update KeenTool action to migrate the complete suite. Pinned alpha installations run bootstrap.sh once. Publish the reviewed complete suite assets before merging the replacement manager into main; component upgrades require the coordinated runtime. A draft release is deliberately not offered to router users. Advance RELEASE.json suite version for every published bundle.

The historical public updater replaces the manager without retaining its original bytes. A migration rollback therefore restores the migration entry at the suite transaction boundary; it cannot recreate a customized manager that the old updater already overwrote. Existing settings, credentials and databases remain protected by the transactional installer. The standalone alpha bootstrap enters the transaction before replacing the alpha manager.

## Lightweight update overview (2.0.3+)

package-suite.py also builds keentool-VERSION-manifest.json and its SHA-256 sidecar. The overview carries the five component versions and reviewed UPDATE_NOTES.json changes. Publish these alongside the complete archive; normal checks verify the overview against its GitHub release asset digest before displaying it. Do not remove or replace these assets after publication. The approved overview must match RELEASE.json in the archive. The source kit builder and GitHub draft workflow use the same package builder.
