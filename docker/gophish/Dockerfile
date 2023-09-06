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

# Stripping X-Gophish 
RUN sed -i 's/X-Gophish-Contact/X-Contact/g' build/models/maillog.go
RUN sed -i 's/X-Gophish-Contact/X-Contact/g' build/models/maillog_test.go
RUN sed -i 's/X-Gophish-Contact/X-Contact/g' build/models/email_request.go
RUN sed -i 's/X-Gophish-Contact/X-Contact/g' build/models/email_request_test.go
# Stripping X-Gophish-Signature
RUN sed -i 's/X-Gophish-Signature/X-Signature/g' build/webhook/webhook.go
# Changing servername
RUN sed -i 's/const ServerName = "gophish"/const ServerName = "Microsoft Outlook 16.0"/' build/config/config.go
# Changing rid value
RUN sed -i 's/const RecipientParameter = "rid"/const RecipientParameter = "SESSGUID"/g' build/models/campaign.go
# Patch phish.go 404.html
COPY "phish.go.patch" "/build/controllers/"
RUN patch "/build/controllers/phish.go" < "/build/controllers/phish.go.patch"
COPY "404.html" "/build/templates/"

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
