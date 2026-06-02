# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar código
COPY . .

# Build com Vite
RUN npm run build

# Stage 2: Runtime (nginx)
FROM nginx:alpine

# Copiar configuração nginx
COPY ./nginx.conf /etc/nginx/nginx.conf

# Copiar build do stage anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Expor porta
EXPOSE 80

# Iniciar nginx
CMD ["nginx", "-g", "daemon off;"]
