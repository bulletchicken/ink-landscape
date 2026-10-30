# Project history

This repository began as the `landscape/` directory in [bulletchicken/bulletchicken](https://github.com/bulletchicken/bulletchicken). Its existing Git history was extracted with `git subtree split --prefix=landscape`; the project was not flattened into a single initial commit.

All seven original commits that changed the landscape are retained, including the two automated data refreshes. Their author and committer identities, timestamps, and complete commit messages were preserved. The extracted files now live at this repository's root, so their trees, ancestry, and commit hashes differ from the originals. Unrelated profile, biography, city, and 3D calendar history was not imported.

The original workflow lived outside `landscape/`, under `.github/workflows/commit-landscape.yml`. Every commit that changed it also changed the landscape, so no additional workflow-only commits were omitted. The workflow itself is adapted for the standalone repository in a subsequent setup commit.

## Original and extracted commits

| Change | Original profile commit | Commit in this repository |
| --- | --- | --- |
| Initial green landscape | [155ea7518a40c18ed0950a192fc971deac907b10](https://github.com/bulletchicken/bulletchicken/commit/155ea7518a40c18ed0950a192fc971deac907b10) | [c9342ef494a5f233c74f7f2e4e8cb4325465e456](https://github.com/bulletchicken/ink-landscape/commit/c9342ef494a5f233c74f7f2e4e8cb4325465e456) |
| Automated commit-data refresh | [ebf21da9a143dfb1bdb149d46513173c50aca389](https://github.com/bulletchicken/bulletchicken/commit/ebf21da9a143dfb1bdb149d46513173c50aca389) | [ba98ba732bb3cc9deabfcd07ae93aa5e555ff0d7](https://github.com/bulletchicken/ink-landscape/commit/ba98ba732bb3cc9deabfcd07ae93aa5e555ff0d7) |
| Monochrome ink and dark background fade | [4570292ddabac321224c27656707746416b7145f](https://github.com/bulletchicken/bulletchicken/commit/4570292ddabac321224c27656707746416b7145f) | [01515c78df29789f9ead0282f96337b3dd259085](https://github.com/bulletchicken/ink-landscape/commit/01515c78df29789f9ead0282f96337b3dd259085) |
| White paper and black outlines | [cb1824dc5b096a9ae097e4a22aa512ceab8b0c22](https://github.com/bulletchicken/bulletchicken/commit/cb1824dc5b096a9ae097e4a22aa512ceab8b0c22) | [9e21f7b3291e1da658690dcd1188de39479beaea](https://github.com/bulletchicken/ink-landscape/commit/9e21f7b3291e1da658690dcd1188de39479beaea) |
| Full profile contributions and varied fish jumps | [f3eae71833edd69cc79959a0f7cba34b4d1ecc6a](https://github.com/bulletchicken/bulletchicken/commit/f3eae71833edd69cc79959a0f7cba34b4d1ecc6a) | [bf7ebf3724b5b23009a36d66004c91c60adefef7](https://github.com/bulletchicken/ink-landscape/commit/bf7ebf3724b5b23009a36d66004c91c60adefef7) |
| Automated contribution-data refresh | [1aa0e7986c525ca040c3124f62471cbbaa4ce6f8](https://github.com/bulletchicken/bulletchicken/commit/1aa0e7986c525ca040c3124f62471cbbaa4ce6f8) | [e352fabdc3cc299ec2833d431f77fa8825f7d386](https://github.com/bulletchicken/ink-landscape/commit/e352fabdc3cc299ec2833d431f77fa8825f7d386) |
| Simplified labels; removed header, footer, and day ranges | [fba81edef39a816c24563b714c7a40a7882e05e6](https://github.com/bulletchicken/bulletchicken/commit/fba81edef39a816c24563b714c7a40a7882e05e6) | [1473cc5e9e42024c0de92297cbedcc6b7f5f8a63](https://github.com/bulletchicken/ink-landscape/commit/1473cc5e9e42024c0de92297cbedcc6b7f5f8a63) |

## Earlier experiments

The earlier local sample-data experiments were not Git repositories and had no commit history to extract. Their source and assets are imported as an archive in a new commit, with their sample-data status and third-party attribution retained. That import is not backdated and does not claim to reconstruct commits that never existed. The seven commits above are the actual recorded history of the published landscape; standalone packaging and archive work follow them as new commits.
