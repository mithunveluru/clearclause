FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

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
