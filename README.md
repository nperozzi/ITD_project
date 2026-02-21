

# Electronic Shelves Label System
## How to run Docker Compose?
### Instructions:
These are instruction on how to run the Docker Compose.
1) Make sure to have Docker running in the background.
2) On a terminal, navigate to the location of the `docker-compose.yml` file.
3) Run the Docker Compose:
```
docker compose up --build
```
This will build the containers and connect them.

4) Open a browser and go to:
```
http:\\localhost:5000
```
This will display the frontend.

### __Test:__
Enter a price and press Send. On the website you should see the battery level and on the terminal you should see 
```
tag-1        | Tag display updated: 1
```

