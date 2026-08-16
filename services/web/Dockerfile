FROM node:22-slim

WORKDIR /app

COPY services/web/package.json services/web/package-lock.json* ./
RUN npm install

COPY services/web/ ./

ARG VITE_AGENT_API_URL=http://localhost:8002
ENV VITE_AGENT_API_URL=$VITE_AGENT_API_URL

RUN npm run build

EXPOSE 5173
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"]
