### dev
```docker-compose -f docker-compose-dev.yaml up```

### stream test
```ffmpeg -re -stream_loop -1 -i murino2.mp4 -c:v libx264 -c:a aac -f flv rtmp://localhost:30444/live/stream```

### Environment variables update
To add new .env variable, upd github env variables and .example.env file and run deploy-secrets action from UI
