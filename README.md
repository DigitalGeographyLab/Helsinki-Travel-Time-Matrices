# Helsinki Travel Time Matrices

This repository contains the scripts (and some of the data) to compute travel
time matrices for the Helsinki metropolitan area, in a self-contained Docker
container.

More information will be added here, as the project evolves.


---

The repository at
[srcrep.atc.gr/urbanageeu](https://srcrep.atc.gr/urbanageeu/travel-time-matrices)
is tracking the **upstream repository** at
[github.com/DigitalGeographyLab](https://github.com/DigitalGeographyLab/Helsinki-Travel-Time-Matrices).
<br>**DO NOT PUSH DIRECTLY TO DOWNSTREAM!**

To update the downstream repository, follow the following steps:

- check out downstream repository
- add upstream repository as additional remote
- rebase downstream main from upstream urbanage-release
- push to downstream

```
git clone https://<username>@<access_token>srcrep.atc.gr/urbanageeu/travel-time-matrices.git
cd travel-time-matrices
git remote add upstream git@github.com:DigitalGeographyLab/Helsinki-Travel-Time-Matrices.git
git fetch upstream
git rebase upstream/urbanage-release
git push
```
