# Node.js base image
FROM node:alpine

# Workdir for output
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json .

# Install dependencies
RUN npm install

# Copy code to working directory
COPY . .

# Expose frontend container port
EXPOSE 3000

# Run the app
CMD ["npm", "run", "dev"]
