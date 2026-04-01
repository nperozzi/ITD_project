# Backend Integration Contract
## Purpose
To define the communication interfaces with the backend.
- HTTP REST endpoints exposed by the backend
- Socket.IO events emitted by the backend
- MQTT topics used between backend and gateway/tag flows

## REST Contract
### Health and Utility
#### `GET /`
Response:
```json
{
  "service": "backend",
  "status": "ok"
}
```

#### `GET /battery`
Response:
```json
{
  "battery": 57
}
```
Behavior:
- Reads the last stored battery value for a tag from the database.
- Requires query parameter `tagId`.
- Returns `400` when `tagId` is not a positive integer.
- Returns `404` when the requested tag does not exist.

### Stores

#### `GET /api/stores`
Returns `Store[]`.

#### `GET /api/stores/{storeId}`
Returns one `Store`.

#### `POST /api/stores`
Request:
```json
{
  "name": "Downtown Market"
}
```
Returns created `Store` with HTTP `201`.

#### `PATCH /api/stores/{storeId}`
Partial request:
```json
{
  "name": "Updated Store"
}
```
Returns updated `Store`.

#### `DELETE /api/stores/{storeId}`
Response:
```json
{
  "status": "deleted",
  "id": 1
}
```

### Gateways
#### `GET /api/gateways`
Returns `Gateway[]`.

#### `GET /api/gateways/{gatewayId}`
Returns one `Gateway`.

#### `POST /api/gateways`
Request:
```json
{
  "storeId": null,
  "status": "degraded",
  "lastHeartbeatAt": "2026-03-14T10:30:00Z"
}
```
Returns created `Gateway` with HTTP `201`.

#### `PATCH /api/gateways/{gatewayId}`
Partial request:
```json
{
  "status": "offline",
  "lastHeartbeatAt": "2026-03-15T08:00:00Z"
}
```
Returns updated `Gateway`.

#### `DELETE /api/gateways/{gatewayId}`
Returns deletion confirmation.

### Shelf Locations
#### `GET /api/shelf-locations`
Returns `ShelfLocation[]`.

#### `GET /api/shelf-locations/{shelfLocationId}`
Returns one `ShelfLocation`.

#### `POST /api/shelf-locations`
Request:
```json
{
  "storeId": 1,
  "aisle": 4,
  "level": 2
}
```
Returns created `ShelfLocation` with HTTP `201`.

#### `PATCH /api/shelf-locations/{shelfLocationId}`
Allows partial updates to `storeId`, `aisle`, and `level`.

#### `DELETE /api/shelf-locations/{shelfLocationId}`
Returns deletion confirmation.

### Products
#### `GET /api/products`
Returns `Product[]`.

#### `GET /api/products/{productId}`
Returns one `Product`.

#### `POST /api/products`
Request:
```json
{
  "sku": "SKU-100",
  "name": "Coffee Beans",
  "attributesJson": {
    "origin": "Kenya"
  },
  "price": 18.5
}
```
Returns created `Product` with HTTP `201`.

#### `PATCH /api/products/{productId}`
Allows partial updates to `sku`, `name`, `attributesJson`, and `price`.

Behavior:
- When a product is updated, the backend also generates and publishes new tag payloads for all tags currently assigned to that product.
- Published payloads are stored in the `tag_payloads` table with `acknowledged=false`.

#### `DELETE /api/products/{productId}`
Returns deletion confirmation.

### Tags
#### `GET /api/tags`
Returns `Tag[]`.

#### `GET /api/tags/{tagId}`
Returns one `Tag`.

#### `POST /api/tags`
Request:
```json
{
  "status": "active",
  "batteryPct": 90,
  "productId": 1,
  "shelfLocationId": null
}
```
Returns created `Tag` with HTTP `201`.

#### `PATCH /api/tags/{tagId}`
Allows partial updates to `batteryPct`, `status`, `productId`, and `shelfLocationId`.

#### `DELETE /api/tags/{tagId}`
Returns deletion confirmation.

#### `POST /api/tags/{tagId}/publish`

Response:

```json
{
  "status": "published",
  "tagId": 1,
  "tagPayloadId": 3,
  "payload": {
    "tagId": 1,
    "title": "Coffee",
    "finalPrice": 9.0
  }
}
```
Behavior:
- Generates the payload for the tag.
- Persists it with `acknowledged=false`.
- Publishes the payload to MQTT topic `b-g/tag{tagId}/payload`.
- Returns `400` if the tag exists but is not assigned to a product.
- Returns `404` if the tag does not exist.

### Tag Payloads
#### `GET /api/tag-payloads`
Returns `TagPayload[]`.

Notes:
- This endpoint is retained for backend inspection use only.

### Promotions
#### `GET /api/promotions`
Returns `Promotion[]`.

#### `GET /api/promotions/{promotionId}`
Returns one `Promotion`.

#### `POST /api/promotions`
Request:
```json
{
  "productId": 1,
  "promoType": "percentage",
  "value": 10,
  "startAt": "2026-03-27T08:00:00Z",
  "endAt": "2026-03-27T20:00:00Z",
  "priority": 1
}
```
Returns created `Promotion` with HTTP `201`.

#### `PATCH /api/promotions/{promotionId}`
Allows partial updates to `productId`, `promoType`, `value`, `startAt`, `endAt`, and `priority`.

#### `DELETE /api/promotions/{promotionId}`
Returns deletion confirmation.

## Socket.IO Contract
Outbound events emitted by backend:

### `battery_update`
Payload:
```json
{
  "tagId": 1,
  "batteryPct": 57,
  "status": "active"
}
```
Behavior:
- Emitted when the backend processes an MQTT battery message.
- Identifies the specific tag whose battery changed.
- Intended for the frontend to update that tag in-place without refetching `/api/tags`.

## MQTT Contract
### Published by Backend
#### `b-g/tag{tagId}/payload`
Payload shape:
```json
{
  "tagId": 1,
  "title": "Coffee",
  "finalPrice": 9.0
}
```
Notes:
- Produced by `POST /api/tags/{tagId}/publish`.
- Also produced indirectly when `PATCH /api/products/{productId}` updates a product assigned to one or more tags.
- Also produced indirectly when a tag is created with a `productId` or when a tag’s `productId` is updated to a new assigned product.

### Subscribed by Backend
#### `b-g/tag{tagId}/advertisement`
Expected incoming payload:
```json
{
  "battery": 42,
  "rssi": -62
}
```

Current backend behavior:
- It reads `battery` from the JSON payload and ignores other advertisement fields it does not use yet.
- It stores the incoming battery value for that specific tag.
- It emits Socket.IO `battery_update` with `tagId`, `batteryPct`, and normalized tag `status`.

#### `b-g/tag{tagId}/ack`
Expected incoming payload:
```json
{
  "tagId": 3,
  "ack": true
}
```
Behavior:
- If `ack` is `true`, the backend marks the latest unacknowledged payload for that tag as acknowledged.
- The backend requires the tag ID in payload field `tagId`.

## Cross-Service Expectations
Frontend expectations:
- Reads REST collections from `/api/stores`, `/api/gateways`, `/api/shelf-locations`, `/api/products`, `/api/tags`, and `/api/promotions`.
- Updates product prices with `PATCH /api/products/{productId}`.
- Listens for Socket.IO `battery_update`.

Gateway or broker-side expectations:

- Consume backend payload snapshots from `b-g/tag{tagId}/payload`.
- Publish acknowledgements to `b-g/tag{tagId}/ack`.
- Publish advertisement messages to `b-g/tag{tagId}/advertisement`.

## Known Implementation Notes
- Currency in generated tag payloads is currently fixed to `EUR`.
- `GET /api/tag-payloads` remains available for smoke tests and backend inspection only.
