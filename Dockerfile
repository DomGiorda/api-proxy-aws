FROM alpine:3.22

WORKDIR /app
COPY src/dotnet-hello.txt ./dotnet-hello.txt

CMD ["sh", "-c", "cat dotnet-hello.txt && sleep 3600"]
