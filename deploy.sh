#! /bin/zsh
set -e
set -x

if ! $(git diff-files --quiet --ignore-submodules --); then
  echo "unstaged files detected"
  exit 1
fi

if [ -n "$(git ls-files --others --exclude-standard)" ]; then
  echo "untracked files detected"
  exit 1
fi

rm -rf ./build ./dist || true

python3 -m venv ./deploy_venv
source ./deploy_venv/bin/activate
python3 -m pip install twine wheel semver

python3 -c '
import semver
with open("./version.txt", "r+") as current_version_fd:
  current_version = current_version_fd.read()
  print(current_version)
  current_version_fd.seek(0)
  new_version = semver.bump_minor(current_version)
  current_version_fd.write(new_version)
  current_version_fd.truncate()
'

python3 ./setup.py sdist bdist_wheel

git add version.txt
git commit -m 'bump version'
git push

git tag v$(cat ./version.txt)
python3 -m twine upload ./dist/*
git push --tag
