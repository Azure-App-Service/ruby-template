FROM {tag}
LABEL maintainer="Azure App Services Container Images <appsvc-images@microsoft.com>"

COPY app /home/site/wwwroot

RUN bundle install \
 && rails server -b 0.0.0.0 -e "$RAILS_ENV" -p "$PORT"

