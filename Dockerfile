FROM scratch

ADD main main
ENTRYPOINT ["/main"]
EXPOSE 80
