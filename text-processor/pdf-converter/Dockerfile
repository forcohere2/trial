# Use the official Node.js LTS version
FROM node:18-slim

# Install necessary dependencies
# Install necessary dependencies
RUN apt-get update && apt-get install -y \
  dumb-init \
  libnss3 \
  libx11-xcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxi6 \
  libxrandr2 \
  libxrender1 \
  libxtst6 \
  ca-certificates \
  fonts-liberation \
  fonts-indic \
  gconf-service \
  libappindicator1 \
  libasound2 \
  libatk1.0-0 \
  libatspi2.0-0 \
  libcups2 \
  libdbus-1-3 \
  libgbm1 \
  libgtk-3-0 \
  libnspr4 \
  libpangocairo-1.0-0 \
  libx11-6 \
  xdg-utils \
  --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /usr/src/app

# Copy the package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 3000
EXPOSE 3000

# Start the server using dumb-init to handle signals
CMD ["dumb-init", "npm", "start"]