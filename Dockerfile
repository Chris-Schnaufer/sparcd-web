
# Build our basic install
FROM node:current-alpine AS build

ENV WORKDIR=/buildsite
WORKDIR ${WORKDIR}

# Install needed tools (won't have an impact if everything is all set)
RUN apk add npm nodejs
RUN npm update -g npm

# Install the package dependencies
COPY ./package.json ./

RUN npm install

# Copy other files where we want them
COPY ./next.config.js ./
COPY ./public ./public
COPY ./app ./app

# Build the node packages
RUN npm run build

# Build the final image
FROM node:current-alpine

ENV WORKDIR=/website
WORKDIR ${WORKDIR}

# Allow Session secret key override
ARG SECRET_KEY=this_is_not_a_secret_key_252627

# Allow port number overrides
ARG PORT_NUMBER=3000

# Allow override of the admin name
ARG ADMIN_NAME=admin

# Allow override of the admin email
ARG ADMIN_EMAIL=admin@arizona.edu

# Copy over the built website
COPY --from=build /buildsite/out ./
RUN mkdir templates
RUN mv index.html templates/

# Install python stuff
COPY ./requirements.txt ./
RUN apk add python3 py-pip
RUN apk add gdal
RUN apk add gdal-dev && \
    apk add python3-dev && \
    apk add gcc g++ && \
    python3 -m pip install --upgrade --no-cache-dir -r requirements.txt --break-system-packages && \
    apk del gcc g++ && \
    apk del python3-dev && \
    apk del gdal-dev

# Copy the source code over
COPY ./server/* ./
COPY ./server/text_formatters ./text_formatters

# Build the default database
RUN rm *.sqlite    # Clean up any testing databases
RUN ./create_db.py --admin ${ADMIN_NAME} --admin_email ${ADMIN_EMAIL} $PWD sparcd.sqlite
RUN rm create_db.py

# Expose the port
EXPOSE ${PORT_NUMBER}

# Setup the gunicorn environment
ENV SERVER_DIR=${WORKDIR} \
    WEB_SITE_URL="0.0.0.0:"${PORT_NUMBER} \
    SPARCD_CODE=${SECRET_KEY} \
    SPARCD_DB=${WORKDIR}/sparcd.sqlite 

ENTRYPOINT gunicorn -w 4 -b ${WEB_SITE_URL} --env SPARCD_DB=${SPARCD_DB} --env SPARCD_CODE=${SPARCD_CODE} --access-logfile '-' sparcd:app --timeout 18000
