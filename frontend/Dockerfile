FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
# ci, not install: reproducible, fails on lockfile drift
RUN npm ci

COPY . .

# NEXT_PUBLIC_* is inlined at build time, not runtime
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# Dev compose overrides this CMD with `npm run dev`
RUN npm run build

# Drop root
RUN chown -R node:node /app
USER node

EXPOSE 3000
CMD ["npm", "run", "start"]
