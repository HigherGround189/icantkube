FROM node:20-alpine AS builder

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install

COPY . .
RUN pnpm run build

FROM busybox:1.36

WORKDIR /dist
COPY --from=builder /app/dist .

EXPOSE 80

CMD ["httpd", "-f", "-p", "80"]
