FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Production build. Dev compose overrides this CMD with `npm run dev` + a
# bind mount, so local development is unaffected; the GHCR image ships prod.
RUN npm run build

# Drop root: the node image ships an unprivileged `node` user (uid 1000).
RUN chown -R node:node /app
USER node

EXPOSE 3000
CMD ["npm", "run", "start"]
