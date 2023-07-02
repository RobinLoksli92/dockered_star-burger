# syntax=docker/dockerfile:1

FROM node:14

WORKDIR /frontend
COPY bundles-src bundles-src
COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm ci --dev

COPY . .
EXPOSE 3000

CMD ["./node_modules/.bin/parcel", "build", "./bundles-src/index.js", "--dist-dir", "bundles", "--public-url", "./" ]