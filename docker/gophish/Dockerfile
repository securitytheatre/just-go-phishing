# syntax=docker/dockerfile:1

# Copyright (C) github.com/securitytheatre
# 
# This file is part of just-go-phishing.
# 
# just-go-phishing is free software: you can redistribute it and/or modify it under the terms of the 
# GNU Affero General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# 
# just-go-phishing is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License along with just-go-phishing. 
# If not, see <https://www.gnu.org/licenses/>.

FROM kalilinux/kali-rolling:latest as build
SHELL ["/bin/bash", "-c"]

RUN apt-get update -yq \
 && DEBIAN_FRONTEND=noninteractive \
    apt-get upgrade -yq \
 && apt-get install -yq git apt-utils net-tools nodejs npm golang jq curl zip \
 && find /var/cache/apt/archives /var/lib/apt/lists -not -name lock -type f -delete

WORKDIR /
RUN git clone https://github.com/gophish/gophish build

COPY "patch" "/patch"
RUN ["bash", "/patch/patch.sh"]

WORKDIR /build
# Minify client-side assets
RUN npm install gulp gulp-cli -g --loglevel verbose
RUN npm install --loglevel verbose
RUN gulp --verbose

WORKDIR /build
# Build the binary
RUN go get -v
RUN go build -v

# Archive and move assets
RUN bash -c "zip -r /assets.zip \
   gophish config.json docker/run.sh VERSION \
   static/js/dist static/js/src/vendor/ckeditor \
   static/css/dist templates static/images static/font \
   static/db db"

# GoPhish stage
FROM kalilinux/kali-rolling:latest as app
SHELL ["/bin/bash", "-c"]

RUN apt-get update -yq \
 && DEBIAN_FRONTEND=noninteractive \
    apt-get upgrade -yq \
 && apt-get install -yq apt-utils net-tools libcap2-bin curl unzip jq \
 && find /var/cache/apt/archives /var/lib/apt/lists -not -name lock -type f -delete

WORKDIR /opt/gophish
# Run phase
COPY --from=build /assets.zip .
RUN unzip assets.zip

EXPOSE 3333 8080 8443 80

CMD ["/bin/bash", "-c", "./docker/run.sh"]
