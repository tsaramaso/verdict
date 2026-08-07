FROM node:22-alpine

WORKDIR /app

ENV NODE_ENV=production

RUN npm install -g bun

COPY package.json bun.lock ./

RUN bun install --frozen-lockfile

COPY . .

RUN bun run build

EXPOSE 4173

CMD ["bun", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]