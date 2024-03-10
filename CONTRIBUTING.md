# Contributing guidelines


- [Making Changes](#making--submitting-changes)
    - [Conventional Commits](#conventional-commits)
    - [Branching Strategy](#branching-strategy)
      - [Release-Please](#release-please)
      - [main branch](#main-branch)
      - [release branch](#release-branch)
    - [CSDL](#csdl)
    - [Product Namings](#product-namings)
- [Publishing to ECR](#publishing-to-ecr)

---

## Making & Submitting Changes

Consider you want to make submit a bugfix into the `main` branch. First you'll want to get the latest code.
Then you'll checkout the desired target branch and create your new branch off of it.

```shell
git checkout master
git pull
git checkout -b update/896703_update_http_traffic_file
```

Create a new branch, ensuring the name is meaningful and uses the allowed prefixes. Allowed prefixes include:

* `$USER/`
* `bugfix/`
* `feature/`

```shell
git checkout -b bugfix/update                      # horrible
git checkout -b bugfix/fix-acl-key-val             # better
git checkout -b bugfix/FWaaS-123-fix-acl-key-val   # best

# make sure your branch is up to date with main
git fetch origin main
git merge origin/main
```

## Conventional Commits

Once you have your branch, you can start committing changes, but **you must follow
[conventional commit](https://www.conventionalcommits.org/en/v1.0.0) guidelines.**

### Commit Types

There are primarily three ways to commit and influence the semantic version:

* `fix`: a commit of the type fix patches a bug in your codebase (this correlates with PATCH in Semantic Versioning).
* `feat`: a commit of the type feat introduces a new feature to the codebase (this correlates with MINOR in Semantic Versioning).
* BREAKING CHANGE: a commit that has a footer BREAKING CHANGE:, or appends a `!` after the type/scope,
  introduces a breaking API change (correlating with MAJOR in Semantic Versioning). 
  A BREAKING CHANGE can be part of commits of any type. See examples below for clarity.

Types other than `fix:` and `feat:` are allowed, 
for example [@commitlint/config-conventional (based on the Angular convention)](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional)
recommends the following:

* `chore`: other changes that don't modify source or test files (will not increment version)
* `refactor`: a code change that neither fixes a bug nor adds a feature
* `build`: changes that affect the build system or external dependencies (will not increment version)
* `ci`: changes to our CI configuration files and scripts (will not increment version)
* `docs`: documentation only changes (will not increment version)
* `revert`: reverts a previous commit
* `style`: changes that do not affect the meaning of the code
* `test`: adding missing tests or correcting existing tests

Any of the above types can declare a breaking change and influence the semantic version. Otherwise, these will not be considered
as a sole reason to create a new release. 

### Examples

#### Commit message with description and breaking change footer
```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

#### Commit message with `!` to draw attention to breaking change
```
feat!: send an email to the customer when a product is shipped
```

#### Commit message with scope and `!` to draw attention to breaking change
```
feat(api)!: send an email to the customer when a product is shipped
```

#### Commit message with both `!` and BREAKING CHANGE footer
```
chore!: Upgrade Go version to 1.20

BREAKING CHANGE: upgrade Go version from 1.18 to 1.20.
```

#### Commit message without a body
```
docs: correct spelling of CHANGELOG
```

#### Commit message with scope
```
feat(ice-cream): FWAAS-XXX add new API for ice cream
```

#### Commit message with multi-paragraph body and multiple footers
```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
```

**All PRs must include a commit message with a description of the changes made!**

Finally, go to GitHub and create a Pull Request.
There should be a PR template already prepared for you.
If not, you will find it at `.github/pull_request_template.md`.
Please describe what this PR is about and add a link to relevant GitHub issues.
If you changed something that is visible to the user, please add a screenshot.
Please follow the
[conventional commit guidelines](https://www.conventionalcommits.org/en/v1.0.0/) for your PR title.

If you only have one commit in your PR, please follow the guidelines for the message
of that single commit, otherwise the PR title is enough.
You can find a list of all possible feature types [here](#commit-types).

An example for a pull request title would be:

```bash
feat(api): New endpoint for feature X (#1234)
```

If you have **breaking changes** in your PR, it is important to note them in the PR
description but also in the merge commit for that PR.

When pressing "squash and merge", you have the option to fill out the commit message.
Please use that feature to add the breaking changes according to the
[conventional commit guidelines](https://www.conventionalcommits.org/en/v1.0.0/).
Also, please remove the PR number at the end and just add the issue number.

An example for a PR with breaking changes and the according merge commit:

```
feat(new-knob): New button that breaks other things (#345)

BREAKING CHANGE: The new button added with #345 introduces new functionality that is not compatible with the previous type of sent events.
```

If your breaking change can be explained in a single line you can also use this form:

```
feat(new-knob)!: New button that breaks other things (#345)
```

Following those guidelines helps us create automated releases where the commit
and PR messages are directly used in the changelog.

In addition, please always ask yourself the following question(s):

* **Based on the linked issue, what changes within the PR would you expect as a reviewer?**

### Test your changes locally

There will be CI/CD running on your eventual pull request, but it is best practice
to test your changes before others spend time reviewing your code.

Nothing is more frustrating than starting a review, only to find that the tests are inadequate or absent.
Very few pull requests can touch the code and NOT touch tests.

This is how you test your code:
- Make sure your code builds, either by building the component you changed, or by building all the components
    - To build only one component run `./gradlew dockerBuild -p<component>` for example `./gradlew dockerBuild -poperator`
    - To build all components run `./gradlew dockerBuild`
- Run unit tests and generate code coverage files on the component you changed, or on all the components
    - To run unit tests on only one component run `./gradlew test -p<component>` for example `./gradlew test -poperator`
    - To run unit tests on all components run `./gradlew test`
- If need be, publish your image(s) to Dockerhub / DevHub
    - To publish the image of only one component run `./gradlew publish -p<component>` for example `./gradlew publish -poperator -PimageTag=<tag>`
    - To publish all images that were built with `tag`, run `./gradlew publish`

**Before submitting a pull request** you should make sure all generated code and go.mod/go.sum have been properly committed.

Before you commit and push, do the following:

```shell
./gradlew tidy format generate generateControllerGenFiles
```
## Branching strategy

This project employs a modified trunk-based development model. In short, this means all pull requests should target the default "main"
branch. [See more info on the trunk model here.](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)

**For the step-by-step guide on publishing official release, please read the [RELEASE doc](./RELEASE.md).**

![branching-diagram](./images/branching.drawio.png)

It differs from the regular trunk model in that `main` acts as a checkpoint for the `release` branch, where official releases
are produced from. Feature branches are also allowed and encouraged.

### Release-Please

Release Please is a tool that automates semantic versioning, release creation, and changelog generation. It parses commit history,
looking for conventional commit messages. It does this with a GitHub Action as part of a two-pass process:

When triggered, it analyzes commit messages to determine the semantic version increase, if any. Then it checks to see if there is 
a "Release PR" currently pending. If not, it will automatically generate the changelog since the last release and submit a
minimal pull request.

Once the Release PR is approved and merged, the action will trigger again. This time, it will understand that a Release PR has been
merged. From here, it knows to push a new git tag and create a GitHub release.

For full details, please visit the [official release-please GitHub repository](https://github.com/googleapis/release-please).

### `main` branch

> **This branch requires linear history, so all PRs targeting this branch should be squash-merged.**

This is the default branch, if you want your code to be in the next release, you must merge it here. The only way new code can be
merged this remote branch is via pull-request. This ensures that every change has been code reviewed before going in.

This branch serves as the integration point for the next release. While no git tags are pushed from this branch, pre-release builds
can still be published from here. In order to create a new official release, `main` must be merged into the `release` branch.

### `release` branch

> PRs targeting this branch **should NOT be squashed**, or else the changelog will lose granularity between releases.

This branch is where official releases and git tags are published from. Once `main` merges into `release`, a 
special "Release PR" is generated with a new proposed semantic version, as well as a CHANGELOG entry containing all the commits 
it discovers as part of the Conventional Commit guidelines mentioned above. This is all handled automatically by 
[Release-Please](https://github.com/googleapis/release-please) via a GitHub Action. 

Once the Release PR is merged into the `release` branch, Release-Please will publish a new tag and GitHub Release, and a new build
(Helm + Docker artifacts) are published with the new semantic version.

### `feature/*` branches

- Peeled out of main branch
- Ideally, these are short-lived
- Features can merge into main only if:
  - the feature is complete and ready to go into a release. That means unit tests, automation, and documentation is in place.
  - there are feature-toggles in place to provide an escape hatch.

### CODEOWNERS

Being a GitHub repository, 
we leverage a [CODEOWNERS file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) 
to automatically add the appropriate people/teams to do code reviews. This is source controlled in the root of the repository and
can be updated as things change or new lines of ownership are formed.

## CI

All new PRs go through CI handled by [GitHub Actions](https://docs.github.com/en/actions). It will run unit tests and code 
coverage checks, build all the Docker files, and publish them to a registry.
Since there are a large number of PR builds at any given time, these artifacts should be considered as ephemeral. They can be 
pruned at any time in order to reduce cost and maintenance burden.

GitHub Actions are executed on self-hosted runners provisioned by an EKS cluster running in the nebula-cicd Streamline account.
For more info on this please refer to the [Action Runner Controller docs](https://github.com/actions/actions-runner-controller),
or our own [Elastic Action Runners repo](https://github.office.opendns.com/nebula/elastic-action-runners) 
which contains the current state of the runner cluster.

### Merge

Decide if this should be a squash or merge commit. Squashing will reduce all changes to a single commit, which is great for a clean and linear history.
Merge commits will retain each individual commit, which can be useful but noisy. As a rule of thumb, it is best to go with squash. But sometimes
keeping granular history might be preferred, such as a long-lived feature branch with many contributors.

Congrats, your code is now in the mainline. By default, branches that get merged will be automatically deleted.

#### PR Builds

The builds generated with PR workflow will be tagged based on pull request number: 1.0.0-PR-{pull_request_number}

#### FIPS-compliant builds

CI will publish both nightly and PR images for modules included in FedRAMP-SFCN with a `-gov` suffix,
e.g., `1.0.0-PR-{pull_request_number}-gov` or `3.0.0-gov`. These images will be available in ECR alongside their
commercial counterparts mentioned above.

## Publishing to ECR

- Helm Charts and docker images generated from Nightly and CI will be published to AWS (023988001120) nebula-cicd ECR.
- We have replication strategy in place which will replicate the image from AWS Cicd to dev, stage, and prod AWS accounts.
- All builds (local, PR and nightly) will be pushed to us-west-2 region 0f CICD account.

### Image Replication Strategy among AWS accounts

GitHub actions will publish builds to nebula-cicd (023988001120) account. From there we have rules in place which will replicate it to other enviroments based on image/profile type.

| profile/image type                       | From Account | From region | To Accounts(s)     | To Region |
| ---------------------------------------- | ------------ | ----------- | ------------------ | --------- |
| local (eng, CEC-personalized, temporary) | 023988001120 | us-west-2   | 662801739978 (dev) | us-west-2 |
| PR (temporary, noisy)                    | 023988001120 | us-west-2   | 662801739978 (dev) <br/> 727671787239 (stage) | us-west-2  |
| nightly (main builds)                    | 023988001120 | us-west-2   | 662801739978 (dev) <br/> 727671787239 (stage) <br/> 241673451830 (prod) | us-west-2 |

### Publishing images from local

We recommend that developers leverage the ECR replication strategy we have set up in order to keep things nice and tidy.

First, request access to the [sfcn-platform-ci-cd-engineers](https://edsart.cloudapps.cisco.com/resources/300214356) IAM group. 
Once you have been added you can generate a session to that account via the following Streamline CLI:

```shell
# the default profile as expressed in gradle is "cicd". You can tell SL to match it so you don't overload your "strln" profile 
sl aws session generate --account-id 023988001120 --role-name ci-cd-engineers --profile cicd
```

Then, you can publish images as you normally would:

```shell
# ecrProfile will default to "cicd". 
# If you set some other profile alias in the previous step, you can override it with "-PecrProfile=myCoolProfileName".
./gradlew publish
```

Once uploaded they'll be automatically mirrored to the accounts according to the table shown above.

### CSDL

If you add a new container, please consider using a distroless image as base image available
here: https://github.com/GoogleContainerTools/distroless or use images hardened by STO team:
https://containers.cisco.com/organization/sto-ccc-cloud9

**Note**: cloud9 doesn't keep any version longer than 6 months.
To use some base image from https://containers.cisco.com/organization/sto-ccc-cloud9, you MUST do next:
1. Pull needed image from STO repository (e.g. `docker pull containers.cisco.com/sto-ccc-cloud9/hardened_alpine:3.15`)
2. Tag it to dockerhub.cisco.com and asac-dev-docker (e.g. `docker tag containers.cisco.com/sto-ccc-cloud9/hardened_alpine:3.15 dockerhub.cisco.com/asac-dev-docker/hardened_alpine:3.15`)
3. Push it (e.g. `docker push dockerhub.cisco.com/asac-dev-docker/hardened_alpine:3.15`)

Then pls use an image, which you pushed to dockerhub.cisco.com/asac-dev-docker.

Add a new image in kASA project here: https://corona.cisco.com/products/6402
Pick appropriate version based on current release, also add image name to:
devtools/corona/main.py so that this container can be scanned for known vulnerabilities.

### Product Namings

* SFCN (Secure Firewall Cloud Native) is the name of the whole product that comprises different services (CNFW, STS), various Kubernetes operators/controllers, the infrastructure to provision the network-optimized Kubernetes cluster on various cloud platforms, etc. Previously, SFCN was referred to as Aegis internally.
* CNFW (Cloud Native Firewall) is one of the services running in SFCN built on top of ASAc. Previously, it was known as kASA.

When naming the components, CRDs, or any other customer-facing resources, keep in mind the distinction between SFCN and CNFW:
* if the component is relevant to all services or represent a generic functionality necessary for all SFCN components (e.g., licensing, Helm templates, upgrade), it should be named as SFCN (e.g., `SmartLicense` CRD has `sfcn.cisco.com` group)
* if the component is specific to the service built around ASAc, it should be named as CNFW (e.g., `ASAConfiguration` CRD has `cnfw.cisco.com` group).

