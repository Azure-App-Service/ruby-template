FROM {tag}
LABEL maintainer="Azure App Services Container Images <appsvc-images@microsoft.com>"

COPY app /home/site/wwwroot

RUN cd /homw/site/wwwroot \
 && bundle update

