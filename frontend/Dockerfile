FROM node:26-alpine

WORKDIR /app

COPY package.json package-lock.json ./
# npm ci installs exactly what the lockfile pins and fails if package.json has
# drifted from it. `npm install` re-resolved versions on every build, so no two
# builds were guaranteed to contain the same dependency tree.
RUN npm ci

COPY . .

# NEXT_PUBLIC_* is inlined into the client bundle at build time, not read at run
# time — so the API URL has to be known here. Defaults to localhost for dev builds;
# the production compose passes the real one.
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# Production build. Dev compose overrides this CMD with `npm run dev` + a
# bind mount, so local development is unaffected; the GHCR image ships prod.
RUN npm run build

# Drop root: the node image ships an unprivileged `node` user (uid 1000).
RUN chown -R node:node /app
USER node

EXPOSE 3000
CMD ["npm", "run", "start"]
