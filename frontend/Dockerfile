FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN node -e "if (!process.env.VITE_API_URL || new URL(process.env.VITE_API_URL).protocol !== 'https:') { throw new Error('Configure VITE_API_URL com o dominio HTTPS da API antes do build.'); }" && npm run build
FROM nginx:alpine
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
ENV PORT=8080
EXPOSE 8080
