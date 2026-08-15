# CI/CD and GitHub Actions Deployment

The AI Research Gap Identifier leverages GitHub actions to enforce CI validation and ensure bad code is never merged into the production branches.

## 1. Existing Workflows

The repository contains a Continuous Integration pipeline explicitly configured within `.github/workflows/ci.yml`.

### Triggers
The CI workflow strictly activates on:
- Commits pushed directly to `main` or `dev`.
- Pull Requests targeting `main` or `dev`.

### Jobs

#### `backend-tests`
- Checks out the repository.
- Initializes Python 3.11 with pip caching.
- Installs all dependencies mapped in `backend/requirements.txt`.
- Executes `pytest backend/tests -q` to validate the backend integrity.

#### `frontend-build`
- Checks out the repository.
- Initializes Node 20.
- Runs `npm ci` inside `./frontend`.
- Runs `npm run build` inside `./frontend` to ensure the Vite compiler successfully maps TypeScript/React into a bundle.

## 2. CD Hook Automation (Render & Vercel)

Deployments are entirely automated outside of GitHub actions natively through Render and Vercel.

- **Vercel Hook**: When the `main` branch is updated on GitHub, Vercel natively catches the webhook payload and automatically kicks off a production build.
- **Render Hook**: Under the Render dashboard settings for your Web Service, ensure **Auto-Deploy** is enabled for the `main` branch. 

## 3. Recommended Branch Protections

To strictly enforce your CI pipelines, you must enable Branch Protections inside the GitHub Repository settings:

1. Navigate to **Settings** > **Branches** > **Add Branch Protection Rule**.
2. **Branch Name Pattern**: `main`
3. Tick **Require pull request reviews before merging**.
4. Tick **Require status checks to pass before merging**.
5. Explicitly search for and require the `backend-tests` and `frontend-build` actions.
6. Tick **Require branches to be up to date before merging**.

This prevents direct pushes to `main` and mandates that your Pytest/Vite builds pass perfectly inside the CI environment prior to Vercel or Render auto-deploying the changes.
