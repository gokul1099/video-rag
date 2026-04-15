FROM node:20.9.0 AS builder

WORKDIR /app

COPY package*.json ./

RUN npm i

COPY . .

# ------------------------------------------------------------

# FROM nginx:alpine

# COPY nginx.conf /etc/nginx/conf.d/default.conf

# COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

CMD ["npm run dev"]