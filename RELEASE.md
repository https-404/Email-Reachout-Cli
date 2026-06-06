# Releasing JobReach

## Prerequisites

```bash
pip install -e ".[dev]"
```

## Local release dry run

```bash
make build          # test + build wheel/sdist
make release-check  # validate dist/ with twine
```

Artifacts land in `dist/`:

- `jobreach-X.Y.Z-py3-none-any.whl`
- `jobreach-X.Y.Z.tar.gz`

## Cut a release

1. Bump the version in both places (keep them in sync):
   - [`pyproject.toml`](pyproject.toml) → `version = "X.Y.Z"`
   - [`jobreach/__init__.py`](jobreach/__init__.py) → `__version__ = "X.Y.Z"`

2. Commit and push:

   ```bash
   git add pyproject.toml jobreach/__init__.py
   git commit -m "Release vX.Y.Z"
   git push
   ```

3. Tag and push the tag:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

4. GitHub Actions (`.github/workflows/release.yml`) will:
   - run tests
   - build the package
   - attach `.whl` and `.tar.gz` to a GitHub Release

## Install from a GitHub Release

```bash
pip install https://github.com/https-404/Email-Reachout-Cli/releases/download/vX.Y.Z/jobreach-X.Y.Z-py3-none-any.whl
```

## Publish to PyPI (optional)

1. Create a project on [PyPI](https://pypi.org) (check that the name `jobreach` is available).
2. Create a [PyPI API token](https://pypi.org/manage/account/token/).
3. In GitHub repo **Settings → Environments**, create an environment named `pypi`.
4. Add secret `PYPI_API_TOKEN` to the `pypi` environment.
5. When a GitHub Release is **published**, `.github/workflows/publish-pypi.yml` uploads to PyPI.

Test on TestPyPI first:

```bash
make build
twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ jobreach
```

## CI

Every push/PR to `main` runs `.github/workflows/ci.yml` (Python 3.11–3.13, tests, build, twine check).
