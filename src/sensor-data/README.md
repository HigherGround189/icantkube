### Variables
S3_ENDPOINT -> RustFS endpoint

BUCKET -> Bucket containing CSV files

REDIS_KEY_PREFIX -> Prefix used to namespace Redis keys

### connect_redis
Check for Redis Database and try to connect to redis. If it pings Redis, it returns the Redis Client and if it fails, it will gracefully fall back.

### get_last_index(name, size)
Retrieves the last served index stated for the dataset, else it will return a random index.

### set_last_index(name, idx)
When connected to Redis, the row after the previous index would pushed.

### load_dataset_by_key
Extracts dataset name from the file, fetches object using boto3. Parse CSV into DictReader and stores them in a CSV_Data and initialize the redis index if not present.

### refresh_dataset_by_name(name)
Used when the dataset was not loaded at the start, or when someone requests it dynamically

### lifespan(app: FastAPI)
Loads all the csv in the bucket and list all files in the bucket. Will fail if no CSV is found

### get("/get_next_line")
If dataset not loaded attempt to refresh, get the last index from Redis and use that index to retrieve the row before computing the next index. The new index would be stored into Redis and return response.

### get("/health")
A quick way to check if the app is running.