FROM node:22-alpine

WORKDIR /workspace

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.base.json eslint.config.mjs .prettierrc.json /workspace/
COPY apps/desktop/package.json /workspace/apps/desktop/package.json
COPY packages/shared/package.json /workspace/packages/shared/package.json
COPY apps/desktop /workspace/apps/desktop
COPY packages/shared /workspace/packages/shared

RUN corepack enable && corepack prepare pnpm@9.12.0 --activate
RUN pnpm install --frozen-lockfile
RUN pnpm --filter @aura/desktop build

EXPOSE 4173

CMD ["sh", "-c", "cd /workspace/apps/desktop && pnpm exec vite preview --host 0.0.0.0 --port 4173"]
