# --- Build stage ---
FROM node:20-alpine AS builder
WORKDIR /app

# Copy manifests
COPY package.json package.json
# If you eventually add a lockfile, COPY package-lock.json as well and switch back to `npm ci`
RUN npm install

# Copy source
COPY . .

# Accept NEXT_PUBLIC_API_URL at build time and set it
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Build
RUN npm run build

# --- Runtime stage ---
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Also set at runtime as a fallback
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Copy build output and minimal runtime files
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./

# Install prod deps for runtime
RUN npm install --omit=dev

EXPOSE 3000
CMD ["npx", "next", "start", "-p", "3000"]
