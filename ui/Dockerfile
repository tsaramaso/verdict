FROM node:22-alpine

WORKDIR /app

ENV NODE_ENV=production

# Install bun
RUN npm install -g bun

# Copy package files
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source
COPY . .

# Build the app
RUN bun run build

# Serve
EXPOSE 5173

CMD ["bun", "run", "preview"]