FROM node:20-alpine

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependências
COPY package.json ./
COPY package-lock.json* ./

# Instala as dependências
RUN npm ci || npm install

# Copia o restante do código
COPY . .

# Expõe a porta do Vite (5173)
EXPOSE 5173

# Comando para rodar o frontend em modo desenvolvimento
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]