FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

# Do not copy source code since we'll mount it via volumes in compose
# COPY . .

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
